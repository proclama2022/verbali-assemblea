# Piano di Correzione - Verbale Approvazione Bilancio

## 🔍 Problemi Identificati

### Problema 1: Ordine del giorno mancante quando si modifica l'anteprima
- **File**: `templates/verbale_assemblea_template.py`
- **Metodo**: `generate_document()` (righe 500-553)
- **Causa**: Quando l'utente modifica l'anteprima, il sistema usa `_create_document_from_text()` che analizza solo il testo ma non include l'ordine del giorno strutturato generato da `_add_bilancio_discussion()`

### Problema 2: Dati delle opzioni non si riportano correttamente
- **File**: `templates/verbale_assemblea_template.py`
- **Metodo**: `_create_document_from_text()` (righe 555-584)
- **Causa**: Il metodo non ha accesso ai dati del form (`data`) quindi non può utilizzare le opzioni selezionate dall'utente

## 🛠️ Soluzioni Proposte

### Soluzione 1: Modificare `_create_document_from_text`
**File**: `templates/verbale_assemblea_template.py`
**Righe**: 555-584

**Modifiche da apportare**:
1. Cambiare la firma del metodo da:
   ```python
   def _create_document_from_text(self, text: str) -> Document:
   ```
   a:
   ```python
   def _create_document_from_text(self, text: str, data: dict) -> Document:
   ```

2. Aggiungere l'ordine del giorno strutturato dopo l'analisi del testo:
   ```python
   # Dopo aver aggiunto le sezioni dal testo
   for section in sections:
       self._add_formatted_section(doc, section)
   
   # Aggiungere sempre l'ordine del giorno strutturato
   self._add_bilancio_discussion(doc, data)
   
   return doc
   ```

### Soluzione 2: Modificare `generate_document`
**File**: `templates/verbale_assemblea_template.py`
**Righe**: 500-553

**Modifiche da apportare**:
1. Alla riga 507, passare i dati al metodo `_create_document_from_text`:
   ```python
   # Da:
   return self._create_document_from_text(st.session_state.final_document_text)
   
   # A:
   return self._create_document_from_text(st.session_state.final_document_text, data)
   ```

### Soluzione 3: Migliorare l'integrazione del testo modificato
**Approccio**: Invece di sostituire completamente il documento con il testo modificato, integrare il testo modificato con le sezioni strutturate essenziali.

**Implementazione**:
1. Analizzare il testo modificato per identificare le sezioni
2. Mantenere sempre le sezioni critiche come:
   - Ordine del giorno (`_add_bilancio_discussion`)
   - Firme (`_add_signatures`)
   - Chiusura (`_add_closing_section`)
3. Utilizzare i dati del form per personalizzare queste sezioni

## 📋 Piano di Implementazione

### Fase 1: Correzione Immediata
1. **Modificare `_create_document_from_text`** per accettare i dati del form
2. **Aggiornare `generate_document`** per passare i dati
3. **Integrare l'ordine del giorno** nel documento generato dal testo

### Fase 2: Miglioramenti Avanzati
1. **Analisi intelligente del testo** per identificare sezioni esistenti
2. **Merge selettivo** tra testo modificato e sezioni strutturate
3. **Validazione coerenza** tra opzioni e contenuto

## 🧪 Test da Eseguire

### Test 1: Generazione normale
- Verificare che il documento si generi correttamente senza modifiche all'anteprima
- Controllare che tutte le opzioni siano riportate correttamente

### Test 2: Modifica anteprima
- Modificare l'anteprima e verificare che:
  - L'ordine del giorno sia presente
  - Le opzioni selezionate siano rispettate
  - Il documento finale sia coerente

### Test 3: Opzioni specifiche
- Testare varie combinazioni di opzioni:
  - Presenza/assenza collegio sindacale
  - Presenza/assenza revisore
  - Modalità di voto
  - Destinazione utili

## 🔧 Codice Specifico da Modificare

### Modifica 1: `_create_document_from_text`
```python
def _create_document_from_text(self, text: str, data: dict) -> Document:
    """Crea un documento Word dal testo modificato dall'utente con formattazione automatica"""
    # ... codice esistente per creare il documento ...
    
    # Analizza la struttura del testo e applica la formattazione automatica
    sections = self._analyze_text_structure(text)
    
    for section in sections:
        self._add_formatted_section(doc, section)
    
    # NUOVO: Aggiungere sempre l'ordine del giorno strutturato
    # Verifica se l'ordine del giorno è già presente nel testo
    if not any('ORDINE DEL GIORNO' in section.get('content', '').upper() for section in sections):
        self._add_bilancio_discussion(doc, data)
    
    return doc
```

### Modifica 2: `generate_document`
```python
def generate_document(self, data: dict) -> Document:
    """Genera il documento Word con formattazione professionale"""
    import streamlit as st
    
    # Controlla se c'è un testo modificato dall'utente nell'anteprima
    if hasattr(st.session_state, 'final_document_text') and st.session_state.final_document_text:
        # MODIFICATO: Passa anche i dati del form
        return self._create_document_from_text(st.session_state.final_document_text, data)
    else:
        # ... resto del codice esistente ...
```

## ✅ Risultati Attesi

Dopo l'implementazione:
1. ✅ L'ordine del giorno sarà sempre presente nel documento finale
2. ✅ Le opzioni selezionate saranno rispettate anche con testo modificato
3. ✅ Il documento manterrà la coerenza tra form e contenuto
4. ✅ La formattazione professionale sarà preservata

## 🚀 Prossimi Passi

1. **Passare alla modalità Code** per implementare le modifiche
2. **Applicare le correzioni** seguendo il piano dettagliato
3. **Testare le modifiche** con vari scenari
4. **Verificare la compatibilità** con altri template