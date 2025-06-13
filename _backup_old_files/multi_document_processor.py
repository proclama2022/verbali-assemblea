from typing import Dict, List, Any, Optional, Tuple
from mistralai import Mistral
import streamlit as st
import json
from typing import Dict, Any
from document_processors import DocumentProcessorFactory

class MultiDocumentProcessor:
    """Processor for handling multiple documents and combining their information"""
    
    def __init__(self, mistral_client: Mistral):
        self.client = mistral_client
        self.processed_documents = []
        self.combined_info = {}
        self.resolved_conflicts = {}  # Store user-resolved conflicts
    
    def process_document(self, file_bytes: bytes, file_name: str, document_type: str) -> Dict[str, Any]:
        """Process a single document and extract information"""
        try:
            # Create processor for the document type
            processor = DocumentProcessorFactory.create_processor(document_type, self.client)
            
            # Extract text based on file type
            if file_name.lower().endswith('.pdf'):
                pypdf2_text, ocr_text = processor.extract_text_from_pdf(file_bytes)
                # Use OCR text if available, fallback to PyPDF2
                document_text = ocr_text if ocr_text else pypdf2_text
            else:
                # Assume text file
                document_text = file_bytes.decode('utf-8')
            
            # Extract information
            if file_name.lower().endswith('.pdf'):
                extracted_info = processor.extract_information(document_text, pdf_bytes=file_bytes)
            else:
                extracted_info = processor.extract_information(document_text)
            
            # Store processed document
            doc_info = {
                'file_name': file_name,
                'document_type': document_type,
                'extracted_info': extracted_info,
                'text_content': document_text
            }
            
            self.processed_documents.append(doc_info)
            return extracted_info
            
        except Exception as e:
            st.error(f"Errore nel processare {file_name}: {e}")
            return {}
    
    def analyze_conflicts_with_ai(self) -> Dict[str, Any]:
        """Use Mistral AI to intelligently analyze conflicts between documents"""
        if len(self.processed_documents) < 2:
            return {"conflicts": [], "analysis": "Nessun conflitto: meno di 2 documenti processati"}
        
        # Prepare document summaries for AI analysis
        docs_summary = []
        for i, doc in enumerate(self.processed_documents, 1):
            docs_summary.append(f"""
DOCUMENTO {i}: {doc['file_name']} (Tipo: {doc['document_type']})
Informazioni estratte:
{json.dumps(doc['extracted_info'], indent=2, ensure_ascii=False)}
""")
        
        analysis_prompt = f"""
Analizza i seguenti {len(self.processed_documents)} documenti e identifica TUTTI i conflitti o discrepanze tra le informazioni estratte.

DOCUMENTI DA ANALIZZARE:
{"".join(docs_summary)}

ISTRUZIONI PER L'ANALISI:
1. Confronta TUTTI i campi simili tra i documenti
2. Identifica conflitti evidenti (valori diversi per lo stesso campo)
3. Segnala discrepanze sospette (es: nomi simili ma non identici)
4. Assegna un livello di confidenza per ogni conflitto (ALTO, MEDIO, BASSO)
5. Suggerisci quale valore potrebbe essere corretto e perché

CAMPI DA CONTROLLARE PRIORITARIAMENTE:
- Denominazione/Nome azienda o persona
- Codice Fiscale/Partita IVA
- Indirizzi e sedi legali
- Date (nascita, costituzione, etc.)
- Numeri di documento
- Importi e valori numerici
- Nomi di persone (amministratori, soci, etc.)

FORMATO OUTPUT:
Rispondi SOLO con un JSON nel seguente formato:
{{
  "conflicts": [
    {{
      "field_name": "nome_campo",
      "conflict_type": "VALORE_DIVERSO|FORMATO_DIVERSO|MISSING_VALUE",
      "confidence_level": "ALTO|MEDIO|BASSO",
      "description": "Descrizione del conflitto",
      "values": [
        {{
          "value": "valore_trovato",
          "source_document": "nome_file",
          "document_type": "tipo_documento",
          "confidence": "perché questo valore potrebbe essere corretto"
        }}
      ],
      "ai_recommendation": "quale valore raccomandi e perché"
    }}
  ],
  "summary": "Riassunto generale dell'analisi"
}}
"""
        
        try:
            messages = [{"role": "user", "content": analysis_prompt}]
            chat_response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                temperature=0.1
            )
            
            response_text = chat_response.choices[0].message.content
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_string = response_text[json_start:json_end + 1]
                return json.loads(json_string)
            else:
                return {"conflicts": [], "analysis": "Errore nell'analisi AI: formato risposta non valido"}
                
        except Exception as e:
            st.error(f"Errore nell'analisi AI dei conflitti: {e}")
            return {"conflicts": [], "analysis": f"Errore: {str(e)}"}

    def display_conflict_resolution_ui(self, conflicts_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Display interactive UI for conflict resolution"""
        
        if not conflicts_analysis.get("conflicts"):
            st.success("✅ **Nessun conflitto rilevato!** Tutti i documenti sono coerenti tra loro.")
            return {}
        
        st.warning(f"⚠️ **Trovati {len(conflicts_analysis['conflicts'])} conflitti** che richiedono la tua attenzione:")
        
        # Show AI summary
        if conflicts_analysis.get("summary"):
            with st.expander("📊 Riassunto Analisi AI", expanded=False):
                st.info(conflicts_analysis["summary"])
        
        resolved_conflicts = {}
        
        for i, conflict in enumerate(conflicts_analysis["conflicts"]):
            st.markdown("---")
            
            # Conflict header with confidence level
            confidence_color = {
                "ALTO": "🔴", 
                "MEDIO": "🟡", 
                "BASSO": "🟢"
            }.get(conflict.get("confidence_level", "MEDIO"), "🔵")
            
            st.markdown(f"### {confidence_color} Conflitto {i+1}: **{conflict['field_name']}**")
            st.markdown(f"**Tipo:** {conflict.get('conflict_type', 'N/A')}")
            st.markdown(f"**Livello Confidenza:** {conflict.get('confidence_level', 'N/A')}")
            
            # Description
            if conflict.get("description"):
                st.markdown(f"**Descrizione:** {conflict['description']}")
            
            # Show AI recommendation
            if conflict.get("ai_recommendation"):
                st.info(f"🤖 **Raccomandazione AI:** {conflict['ai_recommendation']}")
            
            # Display options
            st.markdown("#### 📋 Opzioni disponibili:")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                options = []
                option_details = []
                
                for j, value_info in enumerate(conflict.get("values", [])):
                    source_doc = value_info.get("source_document", "Sconosciuto")
                    doc_type = value_info.get("document_type", "N/A")
                    confidence_reason = value_info.get("confidence", "Nessuna spiegazione")
                    value = value_info.get("value", "N/A")
                    
                    option_label = f"📄 {source_doc} ({doc_type}): '{value}'"
                    options.append(option_label)
                    option_details.append({
                        "value": value,
                        "source": source_doc,
                        "type": doc_type,
                        "reason": confidence_reason
                    })
                
                # Add custom value option
                options.append("✏️ Inserisci valore personalizzato")
                options.append("❌ Lascia vuoto (salta questo campo)")
                
                # Selection
                selected_option = st.radio(
                    f"Scegli il valore corretto per **{conflict['field_name']}**:",
                    options,
                    key=f"conflict_resolution_{i}"
                )
                
                # Show details for selected option
                if selected_option and not selected_option.startswith("✏️") and not selected_option.startswith("❌"):
                    selected_index = options.index(selected_option)
                    if selected_index < len(option_details):
                        detail = option_details[selected_index]
                        st.markdown(f"**Motivo:** {detail['reason']}")
                
                # Handle custom input
                if selected_option and selected_option.startswith("✏️"):
                    custom_value = st.text_input(
                        f"Inserisci valore personalizzato per {conflict['field_name']}:",
                        key=f"custom_value_{i}"
                    )
                    if custom_value:
                        resolved_conflicts[conflict['field_name']] = {
                            "value": custom_value,
                            "source": "Inserimento manuale utente",
                            "resolution_type": "custom"
                        }
                elif selected_option and not selected_option.startswith("❌"):
                    # Extract value from selected option
                    selected_index = options.index(selected_option)
                    if selected_index < len(option_details):
                        detail = option_details[selected_index]
                        resolved_conflicts[conflict['field_name']] = {
                            "value": detail["value"],
                            "source": detail["source"],
                            "resolution_type": "selected"
                        }
                elif selected_option and selected_option.startswith("❌"):
                    resolved_conflicts[conflict['field_name']] = {
                        "value": "",
                        "source": "Utente ha scelto di saltare",
                        "resolution_type": "skip"
                    }
            
            with col2:
                # Show confidence indicators
                st.markdown("#### 🎯 Confidence")
                for value_info in conflict.get("values", []):
                    doc_type = value_info.get("document_type", "N/A")
                    confidence_icon = {
                        "visura": "🏢",
                        "riconoscimento": "🆔", 
                        "bilancio": "💰",
                        "fattura": "🧾",
                        "contratto": "📝"
                    }.get(doc_type, "📄")
                    st.markdown(f"{confidence_icon} {doc_type}")
        
        # Store resolved conflicts
        self.resolved_conflicts = resolved_conflicts
        
        if resolved_conflicts:
            st.success(f"✅ Risolti {len(resolved_conflicts)} conflitti!")
            
            with st.expander("🔍 Riepilogo Risoluzioni", expanded=False):
                for field, resolution in resolved_conflicts.items():
                    st.markdown(f"**{field}:** `{resolution['value']}` (da: {resolution['source']})")
        
        return resolved_conflicts

    def combine_documents_with_conflict_resolution(self, target_template: str = "verbale_assemblea_template") -> Dict[str, Any]:
        """Combine documents with intelligent conflict resolution"""
        
        # Step 1: Analyze conflicts with AI
        conflicts_analysis = self.analyze_conflicts_with_ai()
        
        # Step 2: If conflicts exist, show resolution UI
        if conflicts_analysis.get("conflicts"):
            st.markdown("## 🔍 Risoluzione Conflitti")
            st.markdown("L'AI ha rilevato alcuni conflitti tra i documenti. Per favore aiutaci a risolverli:")
            
            resolved_conflicts = self.display_conflict_resolution_ui(conflicts_analysis)
            
            # Wait for user to resolve all conflicts before proceeding
            if not resolved_conflicts:
                st.warning("⏳ Risolvi i conflitti sopra prima di procedere con la combinazione dei documenti.")
                return {}
        
        # Step 3: Combine documents using AI recommendations and user choices
        return self._combine_with_resolutions(target_template, conflicts_analysis)

    def _combine_with_resolutions(self, target_template: str, conflicts_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine documents applying conflict resolutions"""
        
        template_requirements = self._get_template_requirements(target_template)
        
        # Create enhanced prompt that includes conflict resolutions
        combination_prompt = self._create_enhanced_combination_prompt(
            template_requirements, 
            conflicts_analysis, 
            self.resolved_conflicts
        )
        
        try:
            messages = [{"role": "user", "content": combination_prompt}]
            
            chat_response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                temperature=0
            )
            
            response_text = chat_response.choices[0].message.content
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_string = response_text[json_start:json_end + 1]
                self.combined_info = json.loads(json_string)
            else:
                st.error("Impossibile trovare un blocco JSON valido nella risposta di combinazione.")
                
        except Exception as e:
            st.error(f"Errore nella combinazione dei documenti: {e}")
            
        return self._validate_and_clean_combined_data(self.combined_info)

    def _create_enhanced_combination_prompt(self, requirements: Dict[str, List[str]], 
                                          conflicts_analysis: Dict[str, Any], 
                                          resolved_conflicts: Dict[str, Any]) -> str:
        """Create enhanced prompt with conflict resolutions"""
        
        # Prepare documents summary
        docs_summary = []
        for i, doc in enumerate(self.processed_documents, 1):
            docs_summary.append(f"""
DOCUMENTO {i}: {doc['file_name']} (Tipo: {doc['document_type']})
Informazioni estratte:
{json.dumps(doc['extracted_info'], indent=2, ensure_ascii=False)}
""")
        
        # Create detailed field mapping instructions
        field_mapping_instructions = self._create_field_mapping_instructions()
        
        # Create requirements description with specific mapping
        req_description = []
        for category, fields in requirements.items():
            req_description.append(f"**{category.upper()}:** {', '.join(fields)}")
        
        # Add conflict resolutions
        resolutions_text = ""
        if resolved_conflicts:
            resolutions_text = "\n\n🔒 RISOLUZIONI CONFLITTI APPROVATE DALL'UTENTE (USA SEMPRE QUESTI VALORI):\n"
            for field, resolution in resolved_conflicts.items():
                resolutions_text += f"- {field}: '{resolution['value']}' (fonte: {resolution['source']})\n"
        
        prompt = f"""
Sei un esperto nell'estrazione e mappatura di dati aziendali. Hai a disposizione {len(self.processed_documents)} documenti processati e devi creare un set di dati strutturato per il template richiesto.

DOCUMENTI DISPONIBILI:
{"".join(docs_summary)}

CAMPI RICHIESTI DAL TEMPLATE:
{chr(10).join(req_description)}
{resolutions_text}

{field_mapping_instructions}

REGOLE DI MAPPATURA SPECIFICHE:

1. **ESTRAZIONE INTELLIGENTE:**
   - Se trovi "soci" nella visura con quote → mappa in "soci": [lista oggetti con nome, quota_percentuale, quota_euro]
   - Se trovi "amministratori" nella visura → mappa in "amministratori": [lista oggetti con nome, carica]
   - Se trovi dati aziendali (denominazione, sede, cf) → mappa nei campi azienda specifici
   - Se trovi dati bilancio → mappa nei campi bilancio specifici
   - Se trovi dati assemblea (date, luoghi) → mappa nei campi assemblea specifici

2. **PRIORITÀ FONTI:**
   - Dati aziendali: priorità VISURA > altri documenti
   - Dati personali: priorità RICONOSCIMENTO > altri documenti  
   - Dati finanziari: priorità BILANCIO > altri documenti
   - Date assemblea: priorità VERBALI precedenti > altri documenti

3. **FORMATO OUTPUT CORRETTO:**
   - soci: array di oggetti [{{"nome": "...", "quota_percentuale": "...", "quota_euro": "...", "presente": true/false}}]
   - amministratori: array di oggetti [{{"nome": "...", "carica": "...", "presente": true/false}}]
   - sindaci: array di oggetti [{{"nome": "...", "carica": "...", "presente": true/false}}]
   - Campi semplici: stringhe dirette
   - Mai stringhe JSON nelle liste - sempre array di oggetti

4. **CONFLITTI:**
   - Se ci sono risoluzioni utente → USA SEMPRE quelle
   - Altrimenti usa la priorità fonti sopra indicata

ESEMPIO OUTPUT CORRETTO:
{{
  "denominazione": "PARTITAIVA.IT S.R.L.",
  "sede_legale": "TORINO (TO) CORSO F.FERRUCCI, 112 EDIFICIO 1 CAP 10138",
  "codice_fiscale": "12877980016", 
  "forma_giuridica": "società a responsabilità limitata",
  "capitale_sociale": "10.000,00 euro",
  "soci": [
    {{"nome": "Mario Rossi", "quota_percentuale": "50%", "quota_euro": "5000", "presente": true}},
    {{"nome": "Luigi Bianchi", "quota_percentuale": "50%", "quota_euro": "5000", "presente": false}}
  ],
  "amministratori": [
    {{"nome": "Mario Rossi", "carica": "Amministratore Unico", "presente": true}}
  ],
  "sindaci": [],
  "data_assemblea": "2024-03-15",
  "luogo_assemblea": "Sede legale",
  "risultato_esercizio": "25.000,00 euro"
}}

⚠️ IMPORTANTE: 
- NON mettere JSON stringhe nei campi array
- MAPPA sempre i dati dai documenti sorgenti ai campi del template
- USA i nomi dei campi esatti come richiesti dal template
- Se un campo non ha corrispondenza nei documenti, lascialo vuoto ""

Rispondi SOLO con il dizionario JSON finale, senza commenti o spiegazioni.
"""
        
        return prompt

    def _create_field_mapping_instructions(self) -> str:
        """Create detailed instructions for field mapping"""
        return """
📋 MAPPATURA CAMPI DETTAGLIATA:

**DA VISURA CAMERALE:**
- denominazione → denominazione
- sede_legale → sede_legale  
- codice_fiscale → codice_fiscale
- forma_giuridica → forma_giuridica
- capitale_sociale → capitale_sociale
- soci[].nome → soci[].nome
- soci[].quota_percentuale → soci[].quota_percentuale
- soci[].quota_euro → soci[].quota_euro
- amministratori[].nome → amministratori[].nome
- amministratori[].carica → amministratori[].carica
- sindaci[].nome → sindaci[].nome
- sindaci[].carica → sindaci[].carica

**DA DOCUMENTO RICONOSCIMENTO:**
- nome → per completare dati personali in liste
- cognome → per completare dati personali in liste
- codice_fiscale → per validazione/completamento

**DA BILANCIO:**
- data_chiusura → data_chiusura
- risultato_esercizio → risultato_esercizio
- patrimonio_netto → patrimonio_netto
- ricavi → ricavi
- costi → costi
- debiti → debiti

**DA FATTURE/CONTRATTI:**
- numero_fattura → numero_fattura
- fornitore → fornitore
- cliente → cliente
- totale → totale
- data_fattura → data_fattura
"""
    
    def combine_documents_info(self, target_template: str = "verbale_assemblea_template") -> Dict[str, Any]:
        """Combine information from all processed documents for a specific template"""
        if not self.processed_documents:
            return {}
        
        # Define what information is needed for each template
        template_requirements = self._get_template_requirements(target_template)
        
        # Create prompt for combining information
        combination_prompt = self._create_combination_prompt(template_requirements)
        
        try:
            # Send to Mistral for intelligent combination
            messages = [{"role": "user", "content": combination_prompt}]
            
            chat_response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                temperature=0
            )
            
            response_text = chat_response.choices[0].message.content
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_string = response_text[json_start:json_end + 1]
                self.combined_info = json.loads(json_string)
            else:
                st.error("Impossibile trovare un blocco JSON valido nella risposta di combinazione.")
                
        except Exception as e:
            st.error(f"Errore nella combinazione dei documenti: {e}")
            
        return self._validate_and_clean_combined_data(self.combined_info)
    
    def _validate_and_clean_combined_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e pulisce i dati combinati per assicurarsi che siano nel formato corretto"""
        if not data:
            return {}
        
        cleaned_data = data.copy()
        
        # Lista dei campi che devono essere sempre liste di dizionari
        list_fields = ['soci', 'amministratori', 'sindaci', 'righe_fattura', 'note', 'clausole_principali', 'articoli_chiave', 'poteri_amministratori']
        
        for field in list_fields:
            if field in cleaned_data:
                current_value = cleaned_data[field]
                
                # Se non è una lista, prova a convertirla
                if not isinstance(current_value, list):
                    if isinstance(current_value, str):
                        # Se è una stringa, prova a parsare come JSON
                        try:
                            import json
                            parsed = json.loads(current_value)
                            if isinstance(parsed, list):
                                cleaned_data[field] = parsed
                            else:
                                # Se non è una lista, creane una con l'elemento singolo
                                if field in ['soci', 'amministratori', 'sindaci']:
                                    cleaned_data[field] = [{"nome": current_value.strip()}] if current_value.strip() else []
                                else:
                                    cleaned_data[field] = [current_value] if current_value else []
                        except:
                            # Se il parsing fallisce, crea una lista con l'elemento
                            if field in ['soci', 'amministratori', 'sindaci']:
                                cleaned_data[field] = [{"nome": current_value.strip()}] if current_value.strip() else []
                            else:
                                cleaned_data[field] = [current_value] if current_value else []
                    else:
                        # Per altri tipi, wrappa in una lista
                        cleaned_data[field] = [current_value] if current_value else []
                
                # Pulisci e valida gli elementi della lista
                if isinstance(cleaned_data[field], list):
                    cleaned_list = []
                    for item in cleaned_data[field]:
                        if isinstance(item, dict):
                            # Valida struttura per soci/amministratori/sindaci
                            if field == 'soci':
                                validated_item = self._validate_socio_structure(item)
                                if validated_item:
                                    cleaned_list.append(validated_item)
                            elif field in ['amministratori', 'sindaci']:
                                validated_item = self._validate_persona_structure(item)
                                if validated_item:
                                    cleaned_list.append(validated_item)
                            else:
                                cleaned_list.append(item)
                        elif isinstance(item, str) and item.strip():
                            # Converte stringhe in dizionari per soci/amministratori
                            if field in ['soci', 'amministratori', 'sindaci']:
                                cleaned_list.append({"nome": item.strip()})
                            else:
                                cleaned_list.append(item.strip())
                    cleaned_data[field] = cleaned_list
        
        # Assicurati che i campi booleani siano booleani
        boolean_fields = ['presente', 'audioconferenza', 'voto_palese', 'collegio_sindacale', 'revisore']
        for field in boolean_fields:
            if field in cleaned_data:
                value = cleaned_data[field]
                if isinstance(value, str):
                    cleaned_data[field] = value.lower() in ['true', 'si', 'sì', 'yes', '1']
                elif not isinstance(value, bool):
                    cleaned_data[field] = bool(value)
        
        # Pulisci campi numerici
        numeric_fields = ['capitale_sociale', 'risultato_esercizio', 'patrimonio_netto', 'ricavi', 'costi', 'debiti']
        for field in numeric_fields:
            if field in cleaned_data and cleaned_data[field]:
                # Rimuovi caratteri non numerici eccetto virgole, punti e segni
                import re
                value = str(cleaned_data[field])
                # Mantieni il formato originale se già ben formattato
                if re.match(r'^[\d.,\-\s€]+$', value):
                    cleaned_data[field] = value
                else:
                    # Estrai solo numeri, punti e virgole
                    numeric_value = re.sub(r'[^\d.,\-]', '', value)
                    cleaned_data[field] = numeric_value if numeric_value else ""
        
        return cleaned_data
    
    def _validate_socio_structure(self, socio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e normalizza la struttura di un socio"""
        validated = {}
        
        # Nome (obbligatorio)
        if 'nome' in socio_data and socio_data['nome']:
            validated['nome'] = str(socio_data['nome']).strip()
        else:
            return None  # Socio senza nome non è valido
        
        # Quota percentuale
        if 'quota_percentuale' in socio_data:
            quota = str(socio_data['quota_percentuale']).strip()
            if quota and not quota.endswith('%'):
                quota += '%'
            validated['quota_percentuale'] = quota
        else:
            validated['quota_percentuale'] = ""
        
        # Quota in euro
        if 'quota_euro' in socio_data:
            validated['quota_euro'] = str(socio_data['quota_euro']).strip()
        else:
            validated['quota_euro'] = ""
        
        # Presenza (default true per i soci)
        if 'presente' in socio_data:
            validated['presente'] = bool(socio_data['presente'])
        else:
            validated['presente'] = True
            
        return validated
    
    def _validate_persona_structure(self, persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e normalizza la struttura di amministratore/sindaco"""
        validated = {}
        
        # Nome (obbligatorio)
        if 'nome' in persona_data and persona_data['nome']:
            validated['nome'] = str(persona_data['nome']).strip()
        else:
            return None  # Persona senza nome non è valida
        
        # Carica
        if 'carica' in persona_data:
            validated['carica'] = str(persona_data['carica']).strip()
        else:
            validated['carica'] = ""
        
        # Presenza (default true)
        if 'presente' in persona_data:
            validated['presente'] = bool(persona_data['presente'])
        else:
            validated['presente'] = True
            
        return validated
    
    def _get_template_requirements(self, template_type: str) -> Dict[str, List[str]]:
        """Define what information is needed for each template type"""
        requirements = {
            "verbale_assemblea_template": {
                "azienda": [
                    "denominazione", "sede_legale", "codice_fiscale", "forma_giuridica"
                ],
                "governance": [
                    "amministratori", "sindaci", "rappresentante", "presidente_cda"
                ],
                "soci": [
                    "soci", "capitale_sociale"
                ],
                "bilancio": [
                    "data_chiusura", "risultato_esercizio", "patrimonio_netto", 
                    "ricavi", "costi", "debiti"
                ],
                "assemblea": [
                    "data_assemblea", "luogo_assemblea", "ordine_giorno", "presenti"
                ],
                "documenti_riconoscimento": [
                    "nome", "cognome", "codice_fiscale", "tipo_documento"
                ],
                "contratti": [
                    "tipo_contratto", "parte_a", "parte_b", "valore_contratto"
                ]
            },
            "verbale_assemblea_completo": {
                "azienda": [
                    "denominazione", "sede_legale", "codice_fiscale", "forma_giuridica"
                ],
                "governance": [
                    "amministratori", "sindaci", "rappresentante"
                ],
                "soci": [
                    "soci", "capitale_sociale"
                ],
                "bilancio": [
                    "data_chiusura", "risultato_esercizio", "patrimonio_netto",
                    "ricavi", "costi", "debiti", "perdite_cumulate"
                ],
                "ripianamento": [
                    "modalita_ripianamento", "importo_ripianamento", "contributi_soci"
                ],
                "documenti_riconoscimento": [
                    "nome", "cognome", "codice_fiscale", "tipo_documento"
                ],
                "fatture": [
                    "numero_fattura", "fornitore", "cliente", "totale", "data_fattura"
                ]
            },
            "verbale_assemblea_irregolare": {
                "azienda": [
                    "denominazione", "sede_legale", "codice_fiscale", "forma_giuridica"
                ],
                "governance": [
                    "amministratori", "sindaci", "rappresentante"
                ],
                "irregolarita": [
                    "tipo_irregolarita", "descrizione_problema", "azioni_correttive"
                ],
                "documenti_riferimento": [
                    "titolo", "data_documento", "contenuto_principale"
                ]
            }
        }
        
        return requirements.get(template_type, {})
    
    def _create_combination_prompt(self, requirements: Dict[str, List[str]]) -> str:
        """Create a prompt for combining document information"""
        
        # Prepare documents summary
        docs_summary = []
        for i, doc in enumerate(self.processed_documents, 1):
            docs_summary.append(f"""
DOCUMENTO {i}: {doc['file_name']} (Tipo: {doc['document_type']})
Informazioni estratte:
{json.dumps(doc['extracted_info'], indent=2, ensure_ascii=False)}
""")
        
        # Create requirements description
        req_description = []
        for category, fields in requirements.items():
            req_description.append(f"- {category}: {', '.join(fields)}")
        
        prompt = f"""
Hai a disposizione {len(self.processed_documents)} documenti processati. Combina le informazioni estratte per creare un unico set di dati coerente e completo.

DOCUMENTI DISPONIBILI:
{"".join(docs_summary)}

INFORMAZIONI RICHIESTE PER IL TEMPLATE:
{chr(10).join(req_description)}

ISTRUZIONI PER LA COMBINAZIONE:
1. Estrai SOLO le informazioni rilevanti per il template richiesto
2. Se la stessa informazione è presente in più documenti, usa quella più completa/recente
3. Se un'informazione è assente, lascia il campo vuoto ("")
4. Per liste (soci, amministratori, etc.), combina i dati senza duplicati
5. Mantieni la coerenza tra i documenti (es: stessa denominazione)

IMPORTANTE PER LE LISTE:
- SEMPRE restituire liste come array di oggetti JSON, mai come stringhe
- Per soci: [{{"nome": "Mario Rossi", "quota_percentuale": "50%", "quota_euro": "5000", "presente": true}}]
- Per amministratori: [{{"nome": "Luca Bianchi", "carica": "Amministratore Unico", "presente": true}}]
- Se non ci sono elementi nella lista, restituire []

REGOLE DI PRIORITÀ:
- Per i soci: combina quote e informazioni da tutti i documenti, dando priorità ai dati più recenti
- Per gli amministratori: prendi la struttura più aggiornata
- Per i dati finanziari: usa sempre i più recenti
- Per la governance: controlla coerenza tra documenti
- Documenti di riconoscimento: usa per completare dati personali mancanti

FORMATO OUTPUT:
Rispondi SOLO con un dizionario JSON valido. Assicurati che:
- Tutte le liste siano array JSON, non stringhe
- I campi booleani siano true/false, non "true"/"false"
- I numeri siano formattati correttamente
- Non ci siano virgole finali negli oggetti JSON

"""
        
        return prompt
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get a summary of processed documents"""
        return {
            "total_documents": len(self.processed_documents),
            "document_types": [doc['document_type'] for doc in self.processed_documents],
            "file_names": [doc['file_name'] for doc in self.processed_documents],
            "has_combined_info": bool(self.combined_info)
        }
    
    def clear_documents(self):
        """Clear all processed documents"""
        self.processed_documents = []
        self.combined_info = {}
    
    def get_document_conflicts(self) -> List[Dict[str, Any]]:
        """Identify potential conflicts between documents"""
        conflicts = []
        
        if len(self.processed_documents) < 2:
            return conflicts
        
        # Check for common fields that might conflict
        common_fields = [
            'denominazione', 'codice_fiscale', 'sede_legale', 'partita_iva',
            'nome', 'cognome', 'data_nascita', 'numero_documento',
            'numero_fattura', 'numero_contratto', 'data_contratto'
        ]
        
        for field in common_fields:
            values = {}
            for doc in self.processed_documents:
                # Handle nested objects (like fornitore.denominazione)
                value = self._extract_nested_value(doc['extracted_info'], field)
                if value:
                    if field not in values:
                        values[field] = []
                    values[field].append({
                        'value': value,
                        'source': doc['file_name']
                    })
            
            # Check for conflicts
            if field in values and len(set(item['value'] for item in values[field])) > 1:
                conflicts.append({
                    'field': field,
                    'values': values[field]
                })
        
        return conflicts
    
    def _extract_nested_value(self, data: dict, field: str):
        """Extract value from nested dictionary structures"""
        if field in data:
            return data[field]
        
        # Check nested structures
        for key, value in data.items():
            if isinstance(value, dict):
                if field in value:
                    return value[field]
            elif isinstance(value, list) and value:
                # Check first item of list if it's a dict
                if isinstance(value[0], dict) and field in value[0]:
                    return value[0][field]
        
        return None
    
    def suggest_document_type(self, file_name: str, text_content: str) -> str:
        """Suggest document type based on filename and content"""
        file_name_lower = file_name.lower()
        text_lower = text_content.lower()
        
        # Check filename patterns (more specific first)
        if any(keyword in file_name_lower for keyword in ['visura', 'camerale', 'cciaa']):
            return 'visura'
        elif any(keyword in file_name_lower for keyword in ['bilancio', 'balance', 'financial']):
            return 'bilancio'
        elif any(keyword in file_name_lower for keyword in ['statuto', 'statute', 'bylaws']):
            return 'statuto'
        elif any(keyword in file_name_lower for keyword in ['fattura', 'invoice', 'bill']):
            return 'fattura'
        elif any(keyword in file_name_lower for keyword in ['contratto', 'contract', 'agreement']):
            return 'contratto'
        elif any(keyword in file_name_lower for keyword in ['carta_identita', 'carta', 'patente', 'passaporto', 'documento_identita']):
            return 'riconoscimento'
        
        # Check content patterns (more specific first)
        if any(keyword in text_lower for keyword in ['camera di commercio', 'registro imprese', 'rea', 'numero rea']):
            return 'visura'
        elif any(keyword in text_lower for keyword in ['stato patrimoniale', 'conto economico', 'bilancio di esercizio']):
            return 'bilancio'
        elif any(keyword in text_lower for keyword in ['statuto sociale', 'articolo', 'assemblea ordinaria', 'capitale sociale']):
            return 'statuto'
        elif any(keyword in text_lower for keyword in ['numero fattura', 'partita iva', 'codice destinatario', 'regime iva']):
            return 'fattura'
        elif any(keyword in text_lower for keyword in ['contratto di', 'parte contraente', 'clausola', 'oggetto del contratto']):
            return 'contratto'
        elif any(keyword in text_lower for keyword in ['nato/a il', 'carta d\'identità', 'patente di guida', 'passaporto', 'rilasciato da']):
            return 'riconoscimento'
        
        # Fallback to less specific patterns
        if any(keyword in text_lower for keyword in ['bilancio', 'ricavi', 'patrimonio']):
            return 'bilancio'
        elif any(keyword in text_lower for keyword in ['fattura', 'iva', 'imponibile']):
            return 'fattura'
        elif any(keyword in text_lower for keyword in ['contratto', 'accordo']):
            return 'contratto'
        elif any(keyword in text_lower for keyword in ['nato', 'codice fiscale', 'rilasciato']):
            return 'riconoscimento'
        
        # Default to generic if no patterns match or content is empty
        return 'generico'

    def extract_template_fields_from_documents(self, target_template: str) -> Dict[str, Any]:
        """Extract template-specific fields from each processed document separately"""
        from document_templates import DocumentTemplateFactory
        
        if not self.processed_documents:
            return {"documents": [], "template_fields": []}
        
        try:
            # Get template requirements
            template_requirements = self._get_template_requirements(target_template)
            all_required_fields = []
            for category_fields in template_requirements.values():
                all_required_fields.extend(category_fields)
            
            results = {
                "template_name": target_template,
                "template_fields": all_required_fields,
                "documents": []
            }
            
            # Process each document to extract template-specific information
            for doc in self.processed_documents:
                doc_result = {
                    "file_name": doc['file_name'],
                    "document_type": doc['document_type'],
                    "template_fields": {},
                    "available_fields": [],
                    "missing_fields": []
                }
                
                # Check which template fields are available in this document
                extracted_info = doc['extracted_info']
                
                for field in all_required_fields:
                    if field in extracted_info and extracted_info[field]:
                        doc_result["template_fields"][field] = extracted_info[field]
                        doc_result["available_fields"].append(field)
                    else:
                        doc_result["missing_fields"].append(field)
                
                # Calculate completeness percentage
                if all_required_fields:
                    completeness = len(doc_result["available_fields"]) / len(all_required_fields) * 100
                    doc_result["completeness_percentage"] = round(completeness, 1)
                else:
                    doc_result["completeness_percentage"] = 0
                
                results["documents"].append(doc_result)
            
            return results
            
        except Exception as e:
            st.error(f"Errore nell'estrazione dei campi template: {e}")
            return {"documents": [], "template_fields": []}

    def create_manual_selection_interface(self, template_extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create interface for manual field selection from multiple documents"""
        
        if not template_extraction_results.get("documents"):
            st.warning("Nessun documento processato per la selezione manuale")
            return {}
        
        st.subheader("🎯 Selezione Rapida Informazioni")
        st.markdown(f"**Template:** {template_extraction_results['template_name']}")
        
        # Initialize session state for manual selections
        if 'manual_selections' not in st.session_state:
            st.session_state.manual_selections = {}
        
        selected_data = {}
        all_fields = template_extraction_results["template_fields"]
        
        # Create a simplified interface with tabs for categories
        field_categories = self._categorize_template_fields(all_fields)
        
        # Create tabs for main categories only
        main_categories = {k: v for k, v in field_categories.items() if v and k in ['azienda', 'soci', 'bilancio', 'assemblea']}
        other_fields = []
        for k, v in field_categories.items():
            if k not in main_categories and v:
                other_fields.extend(v)
        if other_fields:
            main_categories['altri'] = other_fields
        
        if main_categories:
            tab_names = list(main_categories.keys())
            tabs = st.tabs([f"📋 {name.title()}" for name in tab_names])
            
            for tab_idx, (category, category_fields) in enumerate(main_categories.items()):
                with tabs[tab_idx]:
                    self._create_simplified_field_selector(category, category_fields, template_extraction_results, selected_data, tab_idx)
        else:
            # Fallback to simple list if no categorization
            self._create_simplified_field_selector("tutti", all_fields, template_extraction_results, selected_data, 0)
        
        # Quick summary
        if selected_data:
            filled_count = len([v for v in selected_data.values() if v is not None and v != ""])
            total_count = len(all_fields)
            completion = (filled_count / total_count * 100) if total_count > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Compilati", filled_count)
            with col2:
                st.metric("📊 Completamento", f"{completion:.0f}%")
            with col3:
                st.metric("📄 Totali", total_count)
        
        return selected_data

    def _create_simplified_field_selector(self, category: str, fields: List[str], template_extraction_results: Dict[str, Any], selected_data: Dict[str, Any], tab_index: int):
        """Create a simplified field selector for a category"""
        
        if not fields:
            st.info(f"Nessun campo in questa categoria")
            return
        
        st.markdown(f"**Seleziona le informazioni per {category}:**")
        
        for field_idx, field in enumerate(fields):
            # Create unique key using category, tab_index, and field_index
            unique_key = f"manual_select_{category}_{tab_index}_{field_idx}_{field}"
            
            st.markdown(f"#### 🔸 {field.replace('_', ' ').title()}")
            
            # Collect options from all documents
            options = ["🚫 Non inserire"]
            option_values = [None]
            
            for doc in template_extraction_results["documents"]:
                if field in doc["template_fields"]:
                    value = doc["template_fields"][field]
                    if value:
                        if isinstance(value, (list, dict)):
                            display_value = f"{len(value)} elementi" if isinstance(value, list) else "Oggetto"
                        else:
                            display_value = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
                        
                        option_label = f"📄 {doc['file_name']}: {display_value}"
                        options.append(option_label)
                        option_values.append(value)
            
            # Add manual input option
            options.append("✏️ Inserimento manuale")
            option_values.append("manual_input")
            
            if len(options) > 1:
                # Get previous selection
                previous_selection = st.session_state.manual_selections.get(unique_key, 0)
                if previous_selection >= len(options):
                    previous_selection = 0
                
                # Create columns for more compact layout
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    selected_option_index = st.selectbox(
                        f"Scegli fonte per **{field}**:",
                        range(len(options)),
                        format_func=lambda i: options[i],
                        index=previous_selection,
                        key=unique_key
                    )
                
                with col2:
                    # Show quick preview button for complex data
                    if (selected_option_index > 0 and 
                        selected_option_index < len(option_values) - 1 and
                        isinstance(option_values[selected_option_index], (list, dict))):
                        if st.button("👁️", key=f"preview_{unique_key}", help="Anteprima dati"):
                            st.json(option_values[selected_option_index])
                
                # Store selection
                st.session_state.manual_selections[unique_key] = selected_option_index
                
                # Handle the selection
                if selected_option_index == 0:
                    selected_data[field] = None
                elif options[selected_option_index].startswith("✏️"):
                    manual_value = st.text_input(
                        f"Valore manuale:",
                        key=f"manual_input_{unique_key}",
                        placeholder=f"Inserisci {field}..."
                    )
                    selected_data[field] = manual_value if manual_value else None
                else:
                    selected_data[field] = option_values[selected_option_index]
            else:
                st.info(f"Campo **{field}** non trovato nei documenti")
                selected_data[field] = None
            
            st.markdown("---")

    def _categorize_template_fields(self, fields: List[str]) -> Dict[str, List[str]]:
        """Categorize template fields for better organization"""
        categories = {
            "azienda": [],
            "governance": [],
            "soci": [],
            "assemblea": [],
            "bilancio": [],
            "documenti": [],
            "contratti": [],
            "altri": []
        }
        
        # Define field patterns for categorization
        patterns = {
            "azienda": ["denominazione", "sede", "codice_fiscale", "partita_iva", "capitale"],
            "governance": ["amministratori", "rappresentanti", "cariche"],
            "soci": ["soci", "socio", "quota"],
            "assemblea": ["data_assemblea", "luogo_assemblea", "ordine_giorno", "presenti"],
            "bilancio": ["patrimonio", "risultato", "ricavi", "costi", "utile", "perdita", "chiusura"],
            "documenti": ["documento", "riconoscimento", "passaporto", "carta_identita"],
            "contratti": ["contratto", "parte_a", "parte_b", "valore"]
        }
        
        for field in fields:
            field_lower = field.lower()
            categorized = False
            
            for category, pattern_words in patterns.items():
                if any(pattern in field_lower for pattern in pattern_words):
                    categories[category].append(field)
                    categorized = True
                    break
            
            if not categorized:
                categories["altri"].append(field)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}