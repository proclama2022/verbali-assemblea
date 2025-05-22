# Documentazione del Progetto Verbale Assemblea

## Descrizione
Questo progetto è sviluppato per estrarre i dati da un verbale di assemblea utilizzando Mistral OCR, verificare e modificare i dati estratti attraverso un'interfaccia utente, e generare documenti Word utilizzando modelli predefiniti.

## Struttura del Progetto
- `src/`: Contiene il codice sorgente dell'applicazione
  - `main.py`: Punto di ingresso dell'applicazione
  - `ocr_processor.py`: Script per l'elaborazione dei dati OCR
  - `document_generator.py`: Script per la generazione dei documenti Word
  - `ui.py`: Script per l'interfaccia utente web-based
- `docs/`: Contiene la documentazione del progetto
  - `API_DOC.md`: Documentazione API di Mistral OCR
- `tests/`: Contiene i test per l'applicazione

## Strumenti Utilizzati
- **Mistral OCR**: Utilizzato per estrarre i dati dalla visura
- **python-docx**: Biblioteca Python per la generazione di documenti Word
- **Flask**: Framework per la gestione dell'interfaccia utente web

## Prerequisiti
Assicurati di avere installato Python 3.7+ e pip.

## Installazione
1. Clona il repository:
   ```bash
   git clone [URL del repository]
   cd verbali-assemblea
   ```
2. Crea un ambiente virtuale (opzionale ma consigliato):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows usa `venv\Scripts\activate`
   ```
3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura le variabili d'ambiente:
   Crea un file `.env` nella root del progetto e aggiungi il tuo API key di Mistral OCR:
   ```
   MISTRAL_API_KEY=[Il tuo API key]
   ```

## Esecuzione
Avvia l'applicazione:
```bash
python src/main.py
```

## Interfaccia Utente
L'applicciazione fornce un'interfaccia web-based dove è possibile:
- Caricare un verbale di assemblea
- Visualizzare i dati estratti
- Modificare i dati se necessario
- Generare un nuovo documento Word
L'interfaccia è accessibile all'indirizzo: http://localhost:5000

## Contributi
I contributi sono benvenuti! Per contribuire:
1. Fai un fork del progetto
2. Crea un nuovo branch: `git checkout -b feature/your-feature-branch`
3. Effettua le tue modifiche e committale: `git commit -am 'Add your feature'`
4. Push a branch: `git push origin feature/your-feature-branch`
5. Apri una pull request

## Licenza
Questo progetto è concesso in licenza sotto la Licenza MIT.