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
    
    def extract_information(self, text: str) -> Dict[str, Any]:
        """Extract information from document text using AI"""
        default_info = self.get_default_structure()
        prompt = self.get_extraction_prompt(text)
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            chat_response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                temperature=0
            )
            
            response_text = chat_response.choices[0].message.content
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_string = response_text[json_start:json_end + 1]
                extracted_info = json.loads(json_string)
                default_info.update(extracted_info)
            else:
                st.error("Impossibile trovare un blocco JSON valido nella risposta dell'API.")
                
        except json.JSONDecodeError as e:
            st.error(f"Errore nel decodificare la risposta JSON: {e}")
        except Exception as e:
            st.error(f"Errore nell'estrazione delle informazioni: {e}")
        
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
        return f"""Estrai le seguenti informazioni dal documento di riconoscimento (passaporto, carta d'identità, patente), rispondendo SOLO con un dizionario JSON.

IMPORTANTE: Il testo potrebbe essere frammentato o contenere errori OCR. Cerca di interpretare i pattern e ricostruire le informazioni anche se incomplete.

PATTERN COMUNI:
- Passaporto italiano: numero formato YY######A (es: AB1234567)
- Carta d'identità: numero 9 cifre + lettera (es: 123456789A)
- Date spesso in formato DD/MM/YYYY o DD.MM.YYYY
- Luoghi di nascita/residenza spesso in maiuscolo
- Codice fiscale: 16 caratteri alfanumerici

Estrai:
- tipo_documento (es: "Passaporto", "Carta d'Identità", "Patente di Guida")
- numero_documento (cerca pattern di numeri con lettere)
- data_rilascio (formato YYYY-MM-DD se possibile)
- data_scadenza (formato YYYY-MM-DD se possibile, cerca "SCAD" o "VAL")
- ente_rilascio (comune, questura o ministero che ha rilasciato)
- nome (prova a identificare dai pattern di testo)
- cognome (spesso in maiuscolo o prima del nome)
- data_nascita (formato YYYY-MM-DD se possibile, cerca "NATO" o "BORN")
- luogo_nascita (cerca dopo "NATO A" o "BORN IN")
- codice_fiscale (16 caratteri alfanumerici)
- indirizzo (residenza o domicilio, cerca "VIA", "PIAZZA", "CORSO")
- cittadinanza (di solito "ITALIANA" o "ITALIAN")
- note: lista di altre informazioni rilevanti trovate nel documento

Testo del documento (potrebbe contenere errori OCR):
{text}

NOTA: Se non riesci a trovare un'informazione specifica, lascia il campo vuoto (""). 
Non inventare dati, ma interpreta il testo al meglio delle tue capacità.
        
Rispondi SOLO con il dizionario JSON, senza altro testo."""

    def extract_information(self, text: str) -> Dict[str, Any]:
        """Extract information from document text using AI with enhanced strategies for identity documents"""
        default_info = self.get_default_structure()
        
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
            
            try:
                messages = [{"role": "user", "content": simple_prompt}]
                chat_response = self.client.chat.complete(
                    model="mistral-small-latest",
                    messages=messages,
                    temperature=0.3  # Leggermente più creativo per inferenze
                )
                
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
                    
            except Exception as e:
                st.warning(f"Strategia semplificata fallita: {e}")
        
        else:
            # Usa il metodo standard per testi più lunghi
            prompt = self.get_extraction_prompt(text)
            
            messages = [{"role": "user", "content": prompt}]
            
            try:
                chat_response = self.client.chat.complete(
                    model="mistral-small-latest",
                    messages=messages,
                    temperature=0
                )
                
                response_text = chat_response.choices[0].message.content
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start != -1 and json_end != -1:
                    json_string = response_text[json_start:json_end + 1]
                    extracted_info = json.loads(json_string)
                    default_info.update(extracted_info)
                else:
                    st.error("Impossibile trovare un blocco JSON valido nella risposta dell'API.")
                    
            except json.JSONDecodeError as e:
                st.error(f"Errore nel decodificare la risposta JSON: {e}")
            except Exception as e:
                st.error(f"Errore nell'estrazione delle informazioni: {e}")
        
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
            "generico": DocumentoGenericoProcessor
        }
        
        if document_type.lower() not in processors:
            raise ValueError(f"Tipo documento non supportato: {document_type}")
        
        return processors[document_type.lower()](mistral_client)
    
    @staticmethod
    def get_available_types() -> List[str]:
        return ["visura", "bilancio", "statuto", "riconoscimento", "fattura", "contratto", "generico"]