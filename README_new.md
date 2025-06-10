# 📄 Sistema di Gestione Documenti Legali

Sistema modulare per l'estrazione automatica di informazioni da documenti legali e la generazione di documenti basati su template personalizzabili.

## 🚀 Caratteristiche

- **Estrazione standardizzata**: Sistema modulare per processare diversi tipi di documenti
- **Template personalizzabili**: Aggiungi facilmente nuovi template per la generazione documenti
- **OCR avanzato**: Supporto sia per PDF digitali (PyPDF2) che scansionati (Mistral OCR)
- **Interfaccia intuitiva**: Web app Streamlit con workflow guidato
- **Estensibilità**: Architettura modulare facilmente estendibile

## 📁 Struttura del Progetto

```
├── src/                           # Codice sorgente principale
│   ├── document_processors.py     # Processori per tipi di documento
│   ├── document_templates.py      # Sistema base per template
│   └── load_templates.py          # Caricatore automatico template
├── templates/                     # Template personalizzati
│   └── verbale_assemblea_template.py
├── output/                        # Documenti generati
├── app_new.py                     # Applicazione principale ristrutturata
├── app.py                         # Versione originale (legacy)
├── requirements.txt               # Dipendenze Python
└── README_new.md                  # Questa documentazione
```

## 🛠️ Installazione

1. **Clona il repository** (se non già fatto)

2. **Installa le dipendenze**:
```bash
pip install -r requirements.txt
```

3. **Configura le variabili d'ambiente**:
```bash
# Crea un file .env nella root del progetto
echo "MISTRAL_API_KEY=your_mistral_api_key_here" > .env
```

4. **Esegui l'applicazione**:
```bash
streamlit run app_new.py
```

## 🎯 Come Usare il Sistema

### 1. Carica Documento
- Seleziona il tipo di documento (Visura, Bilancio, Statuto)
- Carica il file PDF o testo
- Scegli il metodo di estrazione (PyPDF2 per PDF digitali, OCR per scansioni)

### 2. Estrai Informazioni
- Clicca "Estrai Informazioni" per analizzare il documento con AI
- Modifica le informazioni estratte nel form dinamico
- Salva le modifiche

### 3. Genera Documento
- Seleziona il template desiderato
- Configura i parametri specifici del documento
- Genera e scarica il documento Word

## 🔧 Aggiungere Nuovi Processori di Documenti

Per aggiungere supporto per un nuovo tipo di documento:

```python
# src/document_processors.py

class NuovoTipoProcessor(DocumentProcessor):
    """Processor per nuovo tipo di documento"""
    
    def get_document_type_name(self) -> str:
        return "Nuovo Tipo"
    
    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "campo1": "",
            "campo2": "",
            "lista_dati": []
        }
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Estrai le informazioni dal documento..."""

# Registra nel factory
DocumentProcessorFactory.register_processor("nuovo_tipo", NuovoTipoProcessor)
```

## 📝 Aggiungere Nuovi Template

Per creare un nuovo template, crea un file nella cartella `templates/`:

```python
# templates/nuovo_template.py

from document_templates import DocumentTemplate, DocumentTemplateFactory
from docx import Document
import streamlit as st

class NuovoTemplate(DocumentTemplate):
    """Template per nuovo tipo di documento"""
    
    def get_template_name(self) -> str:
        return "Nuovo Documento"
    
    def get_required_fields(self) -> List[str]:
        return ["campo1", "campo2"]
    
    def get_form_fields(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea form Streamlit per configurazione"""
        form_data = {}
        form_data["campo1"] = st.text_input("Campo 1", extracted_data.get("campo1", ""))
        form_data["campo2"] = st.text_input("Campo 2", extracted_data.get("campo2", ""))
        return form_data
    
    def generate_document(self, data: Dict[str, Any]) -> Document:
        """Genera documento Word"""
        doc = Document()
        doc.add_heading(f"Documento per {data['campo1']}", 0)
        doc.add_paragraph(f"Contenuto: {data['campo2']}")
        return doc

# Registra il template
DocumentTemplateFactory.register_template("nuovo", NuovoTemplate)
```

Il template verrà automaticamente caricato al riavvio dell'applicazione.

## 🏗️ Architettura del Sistema

### Processori di Documenti
- **DocumentProcessor**: Classe base astratta
- **VisuraCameraleProcessor**: Estrae informazioni da visure camerali
- **BilancioProcessor**: Estrae dati da bilanci
- **StatutoProcessor**: Elabora statuti societari
- **DocumentProcessorFactory**: Pattern factory per creare processori

### Sistema Template
- **DocumentTemplate**: Classe base per template
- **DocumentTemplateFactory**: Registry pattern per template
- **Caricamento automatico**: `load_templates.py` carica tutti i template dalla cartella

### Flusso di Elaborazione
1. **Upload** → Caricamento e estrazione testo
2. **Processing** → Analisi AI con prompt specifici per tipo documento
3. **Editing** → Modifica manuale delle informazioni estratte
4. **Generation** → Creazione documento basato su template

## 🔄 Migrazione dalla Versione Precedente

La nuova versione è completamente compatibile con i dati esistenti:

- `app.py`: Versione originale (mantenuta per compatibilità)
- `app_new.py`: Nuova versione modulare
- I file di output e template esistenti sono preservati

## 🐛 Risoluzione Problemi

### Template non caricati
- Verifica che i file template siano nella cartella `templates/`
- Controlla che i template implementino correttamente la classe base
- Verifica la sintassi Python nei file template

### Errori di estrazione
- Controlla la chiave API Mistral nel file `.env`
- Verifica la qualità del PDF (per OCR)
- Prova metodi di estrazione alternativi

### Problemi di performance
- Per documenti grandi, usa PyPDF2 invece di OCR
- Considera di limitare la lunghezza del testo inviato all'AI

## 🤝 Contribuire

Per aggiungere nuove funzionalità:

1. Crea nuovi processori in `src/document_processors.py`
2. Aggiungi template nella cartella `templates/`
3. Estendi l'interfaccia utente in `app_new.py` se necessario
4. Documenta le modifiche

## 📊 Confronto Versioni

| Caratteristica | Versione Originale | Versione Modulare |
|---------------|--------------------|-------------------|
| Tipi documento | Solo visure | Estensibile |
| Template | Hardcoded | Modulari |
| Architettura | Monolitica | Pattern-based |
| Manutenibilità | Limitata | Alta |
| Estensibilità | Difficile | Facile |

## 🔮 Roadmap Future

- [ ] Supporto per documenti multi-pagina complessi
- [ ] Template con formattazione avanzata
- [ ] Cache intelligente per l'estrazione
- [ ] Validazione automatica dei dati estratti
- [ ] Export in altri formati (PDF, HTML)
- [ ] Interfaccia per creazione template visuali

---

💡 **Suggerimento**: Inizia con la versione modulare (`app_new.py`) per nuovi progetti e usa la versione originale (`app.py`) solo per compatibilità. 