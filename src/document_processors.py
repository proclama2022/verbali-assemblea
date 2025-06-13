from abc import ABC, abstractmethod
import json
from typing import Dict, List, Any, Optional
from mistralai import Mistral
import PyPDF2
import io
import streamlit as st

class DocumentProcessor(ABC):
    """Base class for document processors"""
    
    def __init__(self, mistral_client: Mistral):
        self.client = mistral_client
    
    @abstractmethod
    def get_extraction_prompt(self, text: str) -> str:
        """Generate the extraction prompt for this document type"""
        pass
    
    @abstractmethod
    def get_default_structure(self) -> Dict[str, Any]:
        """Get the default structure for extracted information"""
        pass
    
    @abstractmethod
    def get_document_type_name(self) -> str:
        """Get the document type name for display"""
        pass
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> tuple[str, str]:
        """Extract text using both PyPDF2 and Mistral OCR with improved OCR settings"""
        # PyPDF2 extraction
        pypdf2_text = ""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pypdf2_text += page_text + "\n"
        except Exception as e:
            st.error(f"Errore PyPDF2: {e}")
            pypdf2_text = ""
        
        # Mistral OCR extraction with optimized settings
        ocr_text = ""
        try:
            uploaded_pdf = self.client.files.upload(
                file={
                    "file_name": "document.pdf",
                    "content": pdf_bytes
                },
                purpose="ocr"
            )
            
            # Use enhanced OCR settings for better text extraction
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": self.client.files.get_signed_url(file_id=uploaded_pdf.id).url
                }
            )
            
            # Combina il markdown di tutte le pagine con separatori
            pages_text = []
            for i, page in enumerate(ocr_response.pages):
                page_content = page.markdown.strip()
                if page_content:
                    pages_text.append(f"--- PAGINA {i+1} ---\n{page_content}")
            
            ocr_text = "\n\n".join(pages_text)
            
            # Se il testo OCR è molto breve, potrebbe essere un documento di identità
            # In questo caso, proviamo a estrarre anche informazioni strutturate
            if len(ocr_text.strip()) < 200 and isinstance(self, DocumentoRiconoscimentoProcessor):
                ocr_text += self._extract_identity_document_patterns(ocr_text)
                
        except Exception as e:
            st.error(f"Errore Mistral OCR: {e}")
            ocr_text = ""
        
        return pypdf2_text, ocr_text
    
    def extract_structured_info_with_ocr(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract structured information directly using Mistral OCR Document Annotation"""
        from pydantic import BaseModel, Field
        from mistralai.extra import response_format_from_pydantic_model
        
        try:
            # Upload del PDF
            uploaded_pdf = self.client.files.upload(
                file={
                    "file_name": "document.pdf",
                    "content": pdf_bytes
                },
                purpose="ocr"
            )
            
            # Definisci il modello Pydantic per l'estrazione strutturata
            if isinstance(self, DocumentoRiconoscimentoProcessor):
                class IdentityDocument(BaseModel):
                    nome: str = Field(default="", description="Nome della persona")
                    cognome: str = Field(default="", description="Cognome della persona")
                    data_nascita: str = Field(default="", description="Data di nascita")
                    luogo_nascita: str = Field(default="", description="Luogo di nascita")
                    codice_fiscale: str = Field(default="", description="Codice fiscale")
                    tipo_documento: str = Field(default="", description="Tipo di documento")
                    numero_documento: str = Field(default="", description="Numero del documento")
                    data_rilascio: str = Field(default="", description="Data di rilascio")
                    data_scadenza: str = Field(default="", description="Data di scadenza")
                    ente_rilascio: str = Field(default="", description="Ente di rilascio")
                
                annotation_model = IdentityDocument
            
            elif isinstance(self, VisuraCameraleProcessor):
                class VisuraCamerale(BaseModel):
                    denominazione: str = Field(default="", description="Denominazione sociale")
                    sede_legale: str = Field(default="", description="Sede legale")
                    pec: str = Field(default="", description="Indirizzo PEC")
                    codice_fiscale: str = Field(default="", description="Codice fiscale")
                    forma_giuridica: str = Field(default="", description="Forma giuridica")
                    rappresentante: str = Field(default="", description="Rappresentante legale")
                    capitale_sociale: str = Field(default="", description="Capitale sociale")
                
                annotation_model = VisuraCamerale
            
            else:
                # Modello generico per altri tipi di documento
                class GenericDocument(BaseModel):
                    content: str = Field(default="", description="Contenuto principale del documento")
                    key_information: str = Field(default="", description="Informazioni chiave estratte")
                
                annotation_model = GenericDocument
            
            # Usa Document Annotation per estrarre informazioni strutturate
            st.info("🔍 Estrazione strutturata con Mistral OCR Document Annotation...")
            
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": self.client.files.get_signed_url(file_id=uploaded_pdf.id).url
                },
                document_annotation_format=response_format_from_pydantic_model(annotation_model)
            )
            
            # Estrai le informazioni strutturate dalla risposta
            if hasattr(ocr_response, 'document_annotation') and ocr_response.document_annotation:
                structured_info = ocr_response.document_annotation
                st.success("✅ Estrazione strutturata completata con successo!")
                return structured_info
            else:
                st.warning("⚠️ Nessuna informazione strutturata estratta, fallback al metodo tradizionale")
                return None
                
        except Exception as e:
            st.error(f"Errore nell'estrazione strutturata: {e}")
            st.info("🔄 Fallback al metodo di estrazione tradizionale...")
            return None
    
    def extract_information(self, text: str, pdf_bytes: bytes = None) -> Dict[str, Any]:
        """Extract information using Mistral OCR Document Annotation first, then fallback to chat completion"""
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        default_info = self.get_default_structure()
        
        # Prima prova con Document Annotation se abbiamo i bytes del PDF
        if pdf_bytes is not None:
            st.info("🚀 Tentativo di estrazione strutturata con Mistral OCR...")
            structured_info = self.extract_structured_info_with_ocr(pdf_bytes)
            
            if structured_info:
                # Converti il risultato strutturato in dizionario
                if hasattr(structured_info, '__dict__'):
                    extracted_dict = structured_info.__dict__
                elif isinstance(structured_info, dict):
                    extracted_dict = structured_info
                else:
                    extracted_dict = {}
                
                # Aggiorna le informazioni di default con quelle estratte
                for key, value in extracted_dict.items():
                    if key in default_info and value and str(value).strip():
                        default_info[key] = str(value).strip()
                
                # Verifica se abbiamo estratto informazioni significative
                non_empty_fields = sum(1 for v in default_info.values() if v and str(v).strip())
                if non_empty_fields >= 3:  # Se abbiamo almeno 3 campi compilati
                    st.success(f"✅ Estrazione strutturata completata! {non_empty_fields} campi estratti.")
                    return default_info
                else:
                    st.warning("⚠️ Estrazione strutturata parziale, provo con il metodo tradizionale...")
        
        # Fallback al metodo tradizionale con chat completion
        st.info("🔄 Estrazione con chat completion...")
        prompt = self.get_extraction_prompt(text)
        
        messages = [{"role": "user", "content": prompt}]
        
        def make_api_call():
            return self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                temperature=0
            )
        
        # Meccanismo di retry con timeout ridotti per evitare blocchi
        max_retries = 2  # Ridotto a 2 tentativi
        timeouts = [10, 20]  # Timeout molto più bassi
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    st.info(f"🔄 Tentativo {attempt + 1} di {max_retries}...")
                
                current_timeout = timeouts[attempt]
                st.info(f"⏳ Timeout impostato: {current_timeout} secondi")
                
                # Usa ThreadPoolExecutor con timeout progressivo
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(make_api_call)
                    start_time = time.time()
                    
                    try:
                        chat_response = future.result(timeout=current_timeout)
                        elapsed_time = time.time() - start_time
                        st.success(f"✅ Estrazione completata in {elapsed_time:.1f} secondi")
                        
                        response_text = chat_response.choices[0].message.content
                        json_start = response_text.find('{')
                        json_end = response_text.rfind('}')
                        
                        if json_start != -1 and json_end != -1:
                            json_string = response_text[json_start:json_end + 1]
                            extracted_info = json.loads(json_string)
                            default_info.update(extracted_info)
                            return default_info  # Successo, esci dal loop
                        else:
                            st.error("Impossibile trovare un blocco JSON valido nella risposta dell'API.")
                            if attempt == max_retries - 1:
                                break
                                
                    except FutureTimeoutError:
                        elapsed = time.time() - start_time
                        error_msg = f"⏰ Timeout al tentativo {attempt + 1}: L'API non risponde entro {current_timeout}s (elapsed: {elapsed:.1f}s)"
                        if attempt == max_retries - 1:
                            st.error(f"{error_msg}\n\n💡 **Possibili soluzioni:**\n- Verifica la connessione internet\n- Riprova tra qualche minuto\n- Il testo potrebbe essere troppo complesso")
                        else:
                            st.warning(error_msg)
                            time.sleep(3)  # Pausa più lunga prima del retry
                    
            except json.JSONDecodeError as e:
                     error_msg = f"Errore JSON al tentativo {attempt + 1}: {e}"
                     if attempt == max_retries - 1:
                         st.error(f"{error_msg} Impossibile decodificare la risposta.")
                     else:
                         st.warning(error_msg)
                         time.sleep(1)  # Pausa ridotta
                         
            except Exception as e:
                error_msg = f"Errore al tentativo {attempt + 1}: {e}"
                if attempt == max_retries - 1:
                    st.error(f"{error_msg}\n\n🔧 **Debug:** {type(e).__name__}, {len(text)} caratteri")
                else:
                    st.warning(error_msg)
                    time.sleep(1)  # Pausa ridotta
        
        return default_info


class VisuraCameraleProcessor(DocumentProcessor):
    """Processor for Visura Camerale documents"""
    
    def get_document_type_name(self) -> str:
        return "Visura Camerale"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "denominazione": "",
            "sede_legale": "",
            "pec": "",
            "codice_fiscale": "",
            "forma_giuridica": "",
            "rappresentante": "",
            "capitale_sociale": "",
            "soci": [],
            "amministratori": [],
            "sindaci": [],
        }
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le seguenti informazioni dalla visura camerale, rispondendo SOLO con un dizionario JSON:
        - denominazione (nome completo dell'azienda)
        - sede_legale (indirizzo completo)
        - pec (indirizzo PEC)
        - codice_fiscale
        - forma_giuridica
        - rappresentante (nome del rappresentante legale)
        - capitale_sociale (se presente)
        - soci: lista di oggetti con chiavi 'nome', 'quota_percentuale', 'quota_euro' (es: [{{"nome": "Mario Rossi", "quota_percentuale": "50%", "quota_euro": "5000"}}, ...])
        - amministratori: lista di oggetti con chiavi 'nome', 'carica' (es: [{{"nome": "Mario Rossi", "carica": "Amministratore Unico"}}, ...])
        - sindaci: lista di oggetti con chiavi 'nome', 'carica' (es: [{{"nome": "Luca Bianchi", "carica": "Presidente Collegio Sindacale"}}, ...])

        Testo della visura:
        {text}
        
        Rispondi SOLO con il dizionario JSON, senza altro testo."""


class BilancioProcessor(DocumentProcessor):
    """Processor for Bilancio documents"""
    
    def get_document_type_name(self) -> str:
        return "Bilancio"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "denominazione": "",
            "codice_fiscale": "",
            "data_chiusura": "",
            "ricavi": "",
            "costi": "",
            "risultato_esercizio": "",
            "patrimonio_netto": "",
            "debiti": "",
            "crediti": "",
            "immobilizzazioni": "",
            "liquidita": "",
            "note_significative": []
        }
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le seguenti informazioni dal bilancio, rispondendo SOLO con un dizionario JSON:
        - denominazione (nome dell'azienda)
        - codice_fiscale
        - data_chiusura (data di chiusura dell'esercizio)
        - ricavi (totale ricavi)
        - costi (totale costi)
        - risultato_esercizio (utile o perdita)
        - patrimonio_netto
        - debiti (totale debiti)
        - crediti (totale crediti)
        - immobilizzazioni (totale immobilizzazioni)
        - liquidita (disponibilità liquide)
        - note_significative: lista di note importanti dal bilancio

        Testo del bilancio:
        {text}
        
        Rispondi SOLO con il dizionario JSON, senza altro testo."""


class StatutoProcessor(DocumentProcessor):
    """Processor for Statuto documents"""
    
    def get_document_type_name(self) -> str:
        return "Statuto"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "denominazione": "",
            "sede_legale": "",
            "oggetto_sociale": "",
            "capitale_sociale": "",
            "durata": "",
            "organi_amministrativi": "",
            "sistema_amministrazione": "",
            "assemblea_convocazione": "",
            "quorum_assemblea": "",
            "quorum_amministratori": "",
            "poteri_amministratori": [],
            "collegio_sindacale": "",
            "revisore_contabile": "",
            "articoli_chiave": [],
            "note_significative": []
        }
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le seguenti informazioni dallo statuto societario, rispondendo SOLO con un dizionario JSON:
        - denominazione (nome della società)
        - sede_legale
        - oggetto_sociale (descrizione dell'attività)
        - capitale_sociale
        - durata (durata della società)
        - organi_amministrativi (tipo di amministrazione: amministratore unico, consiglio di amministrazione, etc.)
        - sistema_amministrazione (tradizionale, monistico, dualistico)
        - assemblea_convocazione (modalità di convocazione assemblea)
        - quorum_assemblea (quorum costitutivo e deliberativo)
        - quorum_amministratori (se CdA)
        - poteri_amministratori: lista dei principali poteri degli amministratori
        - collegio_sindacale (se presente)
        - revisore_contabile (se presente)
        - articoli_chiave: lista degli articoli più rilevanti con numero e descrizione
        - note_significative: lista di note importanti dallo statuto

        Testo dello statuto:
        {text}
        
        Rispondi SOLO con il dizionario JSON, senza altro testo."""


class DocumentoRiconoscimentoProcessor(DocumentProcessor):
    """Processor for Documento di Riconoscimento (Identity Documents)"""
    
    def get_document_type_name(self) -> str:
        return "Documento di Riconoscimento"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "tipo_documento": "",
            "numero_documento": "",
            "data_rilascio": "",
            "data_scadenza": "",
            "ente_rilascio": "",
            "nome": "",
            "cognome": "",
            "data_nascita": "",
            "luogo_nascita": "",
            "codice_fiscale": "",
            "indirizzo": "",
            "cittadinanza": "",
            "note": []
        }
    
    def _extract_identity_document_patterns(self, text: str) -> str:
        """Estrae pattern specifici per documenti di identità quando l'OCR standard fallisce"""
        import re
        
        enhanced_info = "\n\n--- ANALISI PATTERN DOCUMENTI IDENTITÀ ---\n"
        
        # Pattern per numeri di documento (passaporto, carta identità, ecc.)
        doc_numbers = re.findall(r'\b[A-Z]{2}\d{7}\b|\b[A-Z]\d{8}\b|\b\d{8,9}[A-Z]?\b', text, re.IGNORECASE)
        if doc_numbers:
            enhanced_info += f"Possibili numeri documento: {', '.join(doc_numbers)}\n"
        
        # Pattern per date (formato europeo)
        dates = re.findall(r'\b\d{1,2}[./\-]\d{1,2}[./\-]\d{4}\b', text)
        if dates:
            enhanced_info += f"Date trovate: {', '.join(dates)}\n"
        
        # Pattern per luoghi (iniziano con maiuscola, seguiti da minuscole)
        places = re.findall(r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]*)*\b', text)
        if places and len(places) > 2:  # Filtra solo se ci sono abbastanza risultati
            enhanced_info += f"Possibili luoghi: {', '.join(places[:5])}\n"  # Primi 5
        
        # Pattern per codici fiscali italiani
        cf_pattern = re.findall(r'\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b', text, re.IGNORECASE)
        if cf_pattern:
            enhanced_info += f"Codici fiscali: {', '.join(cf_pattern)}\n"
        
        # Pattern per iniziali o nomi (sequenze di lettere maiuscole)
        initials = re.findall(r'\b[A-Z]{2,}\b', text)
        if initials:
            enhanced_info += f"Possibili iniziali/codici: {', '.join(initials[:10])}\n"
        
        return enhanced_info
    
    def get_extraction_prompt(self, text: str) -> str:
        # Limita drasticamente la lunghezza del testo per evitare timeout
        max_text_length = 2000
        if len(text) > max_text_length:
            # Prendi solo l'inizio del testo per velocizzare l'elaborazione
            text = text[:max_text_length]
            st.info(f"📝 Testo limitato a {max_text_length} caratteri per evitare timeout")
        
        return f"""Estrai dal documento:
- nome, cognome
- data_nascita
- luogo_nascita  
- codice_fiscale
- tipo_documento, numero_documento
- data_rilascio, data_scadenza
- ente_rilascio

Testo: {text}

Rispondi solo JSON."""

    def extract_information(self, text: str, pdf_bytes: bytes = None) -> Dict[str, Any]:
        """Extract information using Mistral OCR Document Annotation first, then enhanced fallback strategies for identity documents"""
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        default_info = self.get_default_structure()
        
        # Prima prova con Document Annotation se abbiamo i bytes del PDF
        if pdf_bytes is not None:
            st.info("🚀 Tentativo di estrazione strutturata con Mistral OCR per documento di identità...")
            structured_info = self.extract_structured_info_with_ocr(pdf_bytes)
            
            if structured_info:
                # Converti il risultato strutturato in dizionario
                if hasattr(structured_info, '__dict__'):
                    extracted_dict = structured_info.__dict__
                elif isinstance(structured_info, dict):
                    extracted_dict = structured_info
                else:
                    extracted_dict = {}
                
                # Aggiorna le informazioni di default con quelle estratte
                for key, value in extracted_dict.items():
                    if key in default_info and value and str(value).strip():
                        default_info[key] = str(value).strip()
                
                # Verifica se abbiamo estratto informazioni significative
                non_empty_fields = sum(1 for v in default_info.values() if v and str(v).strip())
                if non_empty_fields >= 3:  # Se abbiamo almeno 3 campi compilati
                    st.success(f"✅ Estrazione strutturata completata! {non_empty_fields} campi estratti.")
                    if 'note' not in default_info:
                        default_info['note'] = []
                    default_info['note'].append("Estratto con Mistral OCR Document Annotation")
                    return default_info
                else:
                    st.warning("⚠️ Estrazione strutturata parziale, provo con strategie avanzate...")
        
        def make_api_call_with_prompt(prompt, temperature=0):
            messages = [{"role": "user", "content": prompt}]
            return self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                temperature=temperature
            )
        
        # Se il testo è molto breve o sembra incompleto, usiamo strategie multiple
        if len(text.strip()) < 100:
            st.warning("⚠️ Testo estratto molto breve. Usando strategie avanzate di estrazione...")
            
            # Strategia 1: Prompt semplificato per testi frammentati
            simple_prompt = f"""
            Il testo seguente è stato estratto da un documento di identità tramite OCR ma potrebbe essere incompleto o frammentato.
            
            Testo disponibile:
            {text}
            
            Analizza il testo e estrai qualsiasi informazione identificabile, anche parziale.
            Cerca pattern come:
            - Sequenze di numeri che potrebbero essere numeri di documento
            - Date in qualsiasi formato
            - Parole che potrebbero essere nomi o luoghi
            - Codici fiscali (16 caratteri alfanumerici)
            
            Rispondi con un JSON contenente solo i campi che puoi identificare con ragionevole certezza:
            {{"tipo_documento": "", "numero_documento": "", "nome": "", "cognome": "", "data_nascita": "", "codice_fiscale": "", "note": []}}
            """
            
            # Meccanismo di retry con timeout ridotti per strategia avanzata
            max_retries_advanced = 2
            timeouts_advanced = [8, 15]  # Timeout molto ridotti per strategia avanzata
            
            for attempt in range(max_retries_advanced):
                try:
                    if attempt > 0:
                        st.info(f"🔄 Retry strategia avanzata {attempt + 1}/{max_retries_advanced}...")
                    
                    current_timeout = timeouts_advanced[attempt]
                    st.info(f"⏳ Timeout strategia avanzata: {current_timeout} secondi")
                    
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(make_api_call_with_prompt, simple_prompt, 0.3)
                        start_time = time.time()
                        chat_response = future.result(timeout=current_timeout)
                        elapsed_time = time.time() - start_time
                        st.success(f"✅ Estrazione avanzata completata in {elapsed_time:.1f} secondi")
                    
                    response_text = chat_response.choices[0].message.content
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}')
                    
                    if json_start != -1 and json_end != -1:
                        json_string = response_text[json_start:json_end + 1]
                        extracted_info = json.loads(json_string)
                        default_info.update(extracted_info)
                        
                        # Aggiungi nota sul metodo di estrazione
                        if 'note' not in default_info:
                            default_info['note'] = []
                        default_info['note'].append("Estratto con strategia avanzata - testo frammentato")
                        break  # Successo, esci dal loop
                        
                except FutureTimeoutError:
                    elapsed = time.time() - start_time
                    if attempt == max_retries_advanced - 1:
                        st.error(f"⏰ Timeout: L'estrazione avanzata ha fallito tutti i tentativi (elapsed: {elapsed:.1f}s).")
                    else:
                        st.warning(f"⏰ Timeout tentativo {attempt + 1} (elapsed: {elapsed:.1f}s), riprovo...")
                        time.sleep(1)
                except Exception as e:
                    if attempt == max_retries_advanced - 1:
                        st.warning(f"Strategia semplificata fallita definitivamente: {e}")
                    else:
                        st.warning(f"Tentativo {attempt + 1} fallito: {e}")
                        time.sleep(1)
        
        else:
            # Usa il metodo standard per testi più lunghi
            st.info("🔄 Estrazione con chat completion...")
            prompt = self.get_extraction_prompt(text)
            
            # Retry per strategia standard con timeout ridotti
            max_retries = 2
            timeouts = [12, 25]  # Timeout ridotti
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        st.info(f"🔄 Tentativo {attempt + 1} di {max_retries}...")
                    
                    current_timeout = timeouts[attempt]
                    st.info(f"⏳ Timeout impostato: {current_timeout} secondi")
                    
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(make_api_call_with_prompt, prompt, 0)
                        start_time = time.time()
                        
                        try:
                            chat_response = future.result(timeout=current_timeout)
                            elapsed_time = time.time() - start_time
                            st.success(f"✅ Estrazione completata in {elapsed_time:.1f} secondi")
                            
                            response_text = chat_response.choices[0].message.content
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}')
                            
                            if json_start != -1 and json_end != -1:
                                json_string = response_text[json_start:json_end + 1]
                                extracted_info = json.loads(json_string)
                                default_info.update(extracted_info)
                                break  # Successo, esci dal loop
                            else:
                                if attempt == max_retries - 1:
                                    st.error("Impossibile trovare un blocco JSON valido nella risposta dell'API.")
                                else:
                                    st.warning(f"Risposta non valida al tentativo {attempt + 1}, riprovo...")
                                    
                        except FutureTimeoutError:
                             elapsed = time.time() - start_time
                             error_msg = f"⏰ Timeout {current_timeout}s (elapsed: {elapsed:.1f}s)"
                             if attempt == max_retries - 1:
                                 st.error(f"{error_msg}\n\n💡 **Soluzioni:**\n- Verifica connessione internet\n- Documento troppo complesso")
                             else:
                                 st.warning(error_msg)
                                 time.sleep(1)  # Pausa ridotta
                        
                except json.JSONDecodeError as e:
                    error_msg = f"Errore JSON al tentativo {attempt + 1}: {e}"
                    if attempt == max_retries - 1:
                        st.error(f"{error_msg} Impossibile decodificare la risposta.")
                    else:
                        st.warning(error_msg)
                        time.sleep(1)  # Pausa ridotta
                        
                except Exception as e:
                    error_msg = f"Errore al tentativo {attempt + 1}: {e}"
                    if attempt == max_retries - 1:
                        st.error(f"{error_msg}\n\n🔧 **Debug info:**\n- Lunghezza testo: {len(text)} caratteri\n- Tipo errore: {type(e).__name__}")
                    else:
                        st.warning(error_msg)
                        time.sleep(1)  # Pausa ridotta
        
        return default_info


class FatturaProcessor(DocumentProcessor):
    """Processor for Fattura documents"""
    
    def get_document_type_name(self) -> str:
        return "Fattura"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "numero_fattura": "",
            "data_fattura": "",
            "data_scadenza": "",
            "fornitore": {
                "denominazione": "",
                "indirizzo": "",
                "partita_iva": "",
                "codice_fiscale": ""
            },
            "cliente": {
                "denominazione": "",
                "indirizzo": "",
                "partita_iva": "",
                "codice_fiscale": ""
            },
            "righe_fattura": [],
            "imponibile": "",
            "iva": "",
            "totale": "",
            "metodo_pagamento": "",
            "note": ""
        }
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le seguenti informazioni dalla fattura, rispondendo SOLO con un dizionario JSON:
        - numero_fattura
        - data_fattura (formato YYYY-MM-DD se possibile)
        - data_scadenza (formato YYYY-MM-DD se possibile)
        - fornitore: oggetto con chiavi 'denominazione', 'indirizzo', 'partita_iva', 'codice_fiscale'
        - cliente: oggetto con chiavi 'denominazione', 'indirizzo', 'partita_iva', 'codice_fiscale'
        - righe_fattura: lista di oggetti con chiavi 'descrizione', 'quantita', 'prezzo_unitario', 'totale'
        - imponibile (importo totale imponibile)
        - iva (importo IVA)
        - totale (importo totale)
        - metodo_pagamento
        - note (eventuali note o causali)

        Testo della fattura:
        {text}
        
        Rispondi SOLO con il dizionario JSON, senza altro testo."""


class ContrattoProcessor(DocumentProcessor):
    """Processor for Contratto documents"""
    
    def get_document_type_name(self) -> str:
        return "Contratto"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "tipo_contratto": "",
            "numero_contratto": "",
            "data_contratto": "",
            "durata": "",
            "data_inizio": "",
            "data_fine": "",
            "parte_a": {
                "denominazione": "",
                "rappresentante": "",
                "indirizzo": "",
                "partita_iva": "",
                "codice_fiscale": ""
            },
            "parte_b": {
                "denominazione": "",
                "rappresentante": "",
                "indirizzo": "",
                "partita_iva": "",
                "codice_fiscale": ""
            },
            "oggetto": "",
            "valore_contratto": "",
            "condizioni_pagamento": "",
            "clausole_principali": [],
            "note": ""
        }
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le seguenti informazioni dal contratto, rispondendo SOLO con un dizionario JSON:
        - tipo_contratto (es: "Locazione", "Fornitura", "Consulenza", "Lavoro")
        - numero_contratto
        - data_contratto (formato YYYY-MM-DD se possibile)
        - durata (es: "12 mesi", "indeterminato")
        - data_inizio (formato YYYY-MM-DD se possibile)
        - data_fine (formato YYYY-MM-DD se possibile)
        - parte_a: oggetto con chiavi 'denominazione', 'rappresentante', 'indirizzo', 'partita_iva', 'codice_fiscale'
        - parte_b: oggetto con chiavi 'denominazione', 'rappresentante', 'indirizzo', 'partita_iva', 'codice_fiscale'
        - oggetto (oggetto del contratto)
        - valore_contratto (se specificato)
        - condizioni_pagamento
        - clausole_principali: lista delle clausole principali
        - note (eventuali note aggiuntive)

        Testo del contratto:
        {text}
        
        Rispondi SOLO con il dizionario JSON, senza altro testo."""


class VerbaleAssembleaProcessor(DocumentProcessor):
    """Processor for Verbale di Assemblea documents"""

    def get_document_type_name(self) -> str:
        return "Verbale di Assemblea"

    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "data_assemblea_str": "", # es. "13/06/2025"
            "ora_assemblea_str": "",  # es. "10:30"
            "luogo_assemblea": "",    # es. "SEDE SOCIALE CATANIA (CT) VIA GABRIELE D'ANNUNZIO 56 CAP 95128"
            "tipo_assemblea": "",     # es. "Ordinaria", "Straordinaria"
            "presidente_assemblea": "", # es. "PETRALIA ROSARIO"
            "segretario_assemblea": "", # opzionale
            "soci_presenti_raw": "",  # Testo grezzo relativo ai soci presenti e capitale
            "capitale_sociale_totale_str": "", # es. "10000.00" (opzionale, se menzionato)
            "capitale_nominale_str": "", # es. "8000.00" (capitale rappresentato dai presenti)
            "percentuale_capitale_str": "", # es. "80.00" (percentuale del capitale presente)
            "ordine_del_giorno_raw": "", # Testo grezzo dell'ordine del giorno
            "punti_ordine_giorno": [], # Lista dei singoli punti all'OdG
            "delibere_raw": "",       # Testo grezzo delle delibere
            "allegati_raw": "",       # Testo grezzo relativo agli allegati
            "ora_chiusura_str": "",   # es. "12:45" (opzionale)
            "note_verbale": ""        # Eventuali note aggiuntive
        }

    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le seguenti informazioni dal verbale di assemblea, rispondendo SOLO con un dizionario JSON.
Presta particolare attenzione ai formati richiesti per date e ore.
Cerca di estrarre 'capitale_nominale_str' e 'percentuale_capitale_str' dal contesto dei soci presenti.

Informazioni da estrarre:
- data_assemblea_str (data dell'assemblea, es. \"GG/MM/AAAA\")
- ora_assemblea_str (ora di inizio dell'assemblea, es. \"HH:MM\")
- luogo_assemblea (luogo completo dell'assemblea)
- tipo_assemblea (es: \"Ordinaria\", \"Straordinaria\", \"generale\")
- presidente_assemblea (nome del presidente dell'assemblea)
- segretario_assemblea (nome del segretario, se menzionato)
- soci_presenti_raw (la porzione di testo che descrive i soci presenti e il capitale sociale rappresentato)
- capitale_sociale_totale_str (il capitale sociale totale della società, se menzionato, es. \"10000.00\")
- capitale_nominale_str (il valore nominale del capitale sociale rappresentato dai soci presenti, es. \"8000.00\")
- percentuale_capitale_str (la percentuale del capitale sociale rappresentata dai soci presenti, es. \"80.00\" o \"80%\")
- ordine_del_giorno_raw (la porzione di testo che elenca l'ordine del giorno)
- punti_ordine_giorno (lista dei singoli punti all'ordine del giorno come stringhe)
- delibere_raw (la porzione di testo che descrive le delibere prese)
- allegati_raw (la porzione di testo che menziona eventuali allegati)
- ora_chiusura_str (ora di chiusura dell'assemblea, es. \"HH:MM\", se menzionata)
- note_verbale (eventuali altre note o informazioni rilevanti dal verbale)

Testo del verbale:
{text}

Rispondi SOLO con il dizionario JSON, senza altro testo.
"""


class DocumentoGenericoProcessor(DocumentProcessor):
    """Processor for generic documents"""
    
    def get_document_type_name(self) -> str:
        return "Documento Generico"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "titolo": "",
            "tipo_documento": "",
            "data_documento": "",
            "mittente": "",
            "destinatario": "",
            "oggetto": "",
            "contenuto_principale": "",
            "persone_menzionate": [],
            "aziende_menzionate": [],
            "date_importanti": [],
            "importi_menzionati": [],
            "contatti": [],
            "note": ""
        }
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le seguenti informazioni dal documento, rispondendo SOLO con un dizionario JSON:
        - titolo (titolo o oggetto principale del documento)
        - tipo_documento (cerca di identificare il tipo: "Lettera", "Comunicazione", "Verbale", "Relazione", etc.)
        - data_documento (formato YYYY-MM-DD se possibile)
        - mittente (chi ha scritto/inviato il documento)
        - destinatario (a chi è destinato)
        - oggetto (oggetto o argomento principale)
        - contenuto_principale (riassunto del contenuto in 2-3 frasi)
        - persone_menzionate: lista di nomi di persone citate nel documento
        - aziende_menzionate: lista di aziende/organizzazioni citate
        - date_importanti: lista di date rilevanti trovate nel documento
        - importi_menzionati: lista di importi in euro citati
        - contatti: lista di contatti (email, telefoni, indirizzi) trovati
        - note (altre informazioni rilevanti)

        Testo del documento:
        {text}
        
        Rispondi SOLO con il dizionario JSON, senza altro testo."""


class DocumentProcessorFactory:
    """Factory to create document processors"""
    
    @staticmethod
    def create_processor(document_type: str, mistral_client: Mistral) -> DocumentProcessor:
        processors = {
            "visura": VisuraCameraleProcessor,
            "bilancio": BilancioProcessor,
            "statuto": StatutoProcessor,
            "riconoscimento": DocumentoRiconoscimentoProcessor,
            "fattura": FatturaProcessor,
            "contratto": ContrattoProcessor,
            "verbale_assemblea": VerbaleAssembleaProcessor, # Aggiunto nuovo processore
            "generico": DocumentoGenericoProcessor
        }
        
        if document_type.lower() not in processors:
            raise ValueError(f"Tipo documento non supportato: {document_type}")
        
        return processors[document_type.lower()](mistral_client)
    
    @staticmethod
    def get_available_types() -> List[str]:
        return ["visura", "bilancio", "statuto", "riconoscimento", "fattura", "contratto", "verbale_assemblea", "generico"] # Aggiunto nuovo tipo