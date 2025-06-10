# 🔍 Guida per Migliorare l'Estrazione OCR dai Passaporti

## Problemi Comuni con l'OCR sui Documenti di Identità

I passaporti e i documenti di identità scansionati presentano spesso sfide uniche per l'OCR:

### 1. **Qualità dell'Immagine**
- **Problema**: Documenti fotografati con smartphone o scanner di bassa qualità
- **Soluzioni**:
  - Utilizzare scanner ad alta risoluzione (300+ DPI)
  - Illuminazione uniforme senza riflessi
  - Documento piatto e ben allineato

### 2. **Elementi di Sicurezza**
- **Problema**: Filigrane, ologrammi e pattern di sicurezza interferiscono con l'OCR
- **Soluzioni**: 
  - L'OCR avanzato di Mistral è progettato per gestire questi elementi
  - Utilizzare le strategie multi-prompt implementate nel sistema

### 3. **Font e Dimensioni del Testo**
- **Problema**: Font piccoli, caratteri speciali, testo in maiuscolo
- **Soluzioni**: 
  - Il sistema ora utilizza pattern recognition per identificare informazioni anche con OCR parziale

## 🛠️ Miglioramenti Implementati nel Sistema

### 1. **Estrazione OCR Migliorata**
```python
# Il sistema ora:
- Combina PyPDF2 + Mistral OCR
- Separa le pagine con identificatori chiari
- Aggiunge analisi pattern per documenti brevi
- Utilizza strategie multiple per testi frammentati
```

### 2. **Pattern Recognition Avanzato**
Il sistema riconosce automaticamente:
- **Numeri di documento**: `AB1234567` (passaporti), `123456789A` (carte d'identità)
- **Date**: Formati `DD/MM/YYYY`, `DD.MM.YYYY`, `DD-MM-YYYY`
- **Codici fiscali**: Pattern a 16 caratteri alfanumerici
- **Luoghi**: Parole che iniziano con maiuscola
- **Nomi e cognomi**: Sequenze di lettere maiuscole

### 3. **Strategie Multi-Prompt**
Per testi molto brevi (< 100 caratteri), il sistema:
- Utilizza prompt semplificati
- Aumenta la creatività dell'AI (temperature 0.3)
- Cerca informazioni parziali identificabili
- Documenta il metodo di estrazione utilizzato

## 📋 Guida per l'Utente

### **Prima di Scansionare**
1. **Pulire il documento** da polvere e impronte
2. **Posizionare su superficie piana** senza pieghe
3. **Illuminazione uniforme** senza ombre o riflessi
4. **Scansione diretta** (non fotografare lo schermo)

### **Impostazioni Scanner Consigliate**
- **Risoluzione**: 300-600 DPI
- **Formato**: PDF o TIFF
- **Colore**: RGB (non scala di grigi)
- **Compressione**: Minima o nessuna

### **Durante l'Upload**
1. **Seleziona "Documento di Riconoscimento"** come tipo
2. **Confronta PyPDF2 vs OCR Mistral** nei risultati
3. **Scegli il metodo migliore** in base alla qualità del testo estratto
4. **Verifica l'anteprima** prima di procedere

### **Se l'Estrazione Fallisce**
Il sistema implementa questi fallback automatici:
1. **Analisi pattern** per identificare numeri/date anche se frammentati
2. **Prompt semplificato** per inferire informazioni dalle parole riconoscibili
3. **Note di estrazione** per tracciare il metodo utilizzato

## 🎯 Risultati Attesi

### **Passaporto Italiano**
Il sistema dovrebbe estrarre:
- Tipo documento: "Passaporto"
- Numero: Pattern `AB1234567`
- Nome e cognome
- Data di nascita
- Luogo di nascita  
- Data rilascio/scadenza
- Ente rilascio: "REPUBBLICA ITALIANA"

### **Carta d'Identità**
Il sistema dovrebbe estrarre:
- Tipo documento: "Carta d'Identità"
- Numero: Pattern `123456789A`
- Nome e cognome
- Codice fiscale (16 caratteri)
- Data/luogo di nascita
- Indirizzo di residenza
- Comune di rilascio

### **Nota sui Documenti Stranieri**
Per passaporti/documenti non italiani:
- Il sistema si adatta ai pattern locali
- Cerca parole chiave in inglese ("PASSPORT", "BORN", "NATIONALITY")
- Utilizza inferenze basate sulla struttura del documento

## 🔧 Suggerimenti per Casi Difficili

### **Documento Molto Rovinato**
1. Prova multiple scansioni con angolazioni diverse
2. Utilizza la funzione "Documento Generico" se "Riconoscimento" fallisce
3. Completa manualmente i campi mancanti dopo l'estrazione

### **Testo Molto Frammentato**
Il sistema ora:
- Identifica anche informazioni parziali
- Combina frammenti per ricostruire dati completi
- Fornisce note su quali informazioni sono inferite

### **Documenti Bilingui**
- Il sistema riconosce automaticamente testo in italiano e inglese
- Priorizza le informazioni più complete
- Combina dati da sezioni diverse del documento

## 📊 Monitoraggio della Qualità

Il sistema traccia automaticamente:
- **Metodo di estrazione utilizzato** (standard vs. avanzato)
- **Lunghezza del testo estratto** (indicatore di qualità)
- **Pattern riconosciuti** (numeri, date, codici)
- **Campi estratti con successo** vs. campi vuoti

Queste informazioni sono disponibili nelle note del documento elaborato. 