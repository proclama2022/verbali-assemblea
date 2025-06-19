# Diagnosi: Ordine del Giorno Mancante nel Documento Finale

## 🔍 Problema Identificato

Il documento finale mostra:
```
ORDINE DEL GIORNO

Assume la presidenza ai sensi dell'art. […] dello statuto sociale...
```

Ma **mancano i punti dell'ordine del giorno**:
- 1. Approvazione del bilancio d'esercizio al [data]
- 2. Destinazione del risultato d'esercizio

## 🕵️ Analisi del Problema

### Flusso Attuale
1. **Anteprima**: L'ordine del giorno viene mostrato correttamente nel metodo `_generate_preview_text`
2. **Modifica utente**: L'utente può modificare l'anteprima
3. **Generazione documento**: Il metodo `_create_document_from_text` dovrebbe:
   - Analizzare il testo modificato
   - Rilevare se l'ordine del giorno è presente
   - Se mancante, aggiungere l'ordine del giorno strutturato

### Problema nella Logica di Rilevamento

Nel metodo `_create_document_from_text` (riga 588-597):
```python
# Verifica se l'ordine del giorno è già presente nel testo
has_bilancio_discussion = any(
    'ORDINE DEL GIORNO' in section.get('content', '').upper() or
    'BILANCIO' in section.get('content', '').upper() or
    'DELIBERA' in section.get('content', '').upper()
    for section in sections
)

if not has_bilancio_discussion:
    # Aggiungi l'ordine del giorno strutturato
    doc.add_paragraph()
    self._add_bilancio_discussion(doc, data)
```

**Il problema**: La logica rileva che "ORDINE DEL GIORNO" è presente nel testo, quindi NON aggiunge l'ordine del giorno strutturato. Ma il testo contiene solo il titolo "ORDINE DEL GIORNO" senza i punti specifici.

## 🛠️ Soluzioni Proposte

### Soluzione 1: Migliorare la Logica di Rilevamento
Cambiare la condizione per verificare se ci sono i punti specifici dell'ordine del giorno:

```python
# Verifica se i punti specifici dell'ordine del giorno sono presenti
has_bilancio_points = any(
    'Approvazione del bilancio' in section.get('content', '') or
    'approvazione del bilancio' in section.get('content', '') or
    'DELIBERA' in section.get('content', '').upper()
    for section in sections
)
```

### Soluzione 2: Sempre Aggiungere l'Ordine del Giorno Strutturato
Rimuovere completamente la logica di rilevamento e sempre aggiungere l'ordine del giorno strutturato:

```python
# Aggiungi sempre l'ordine del giorno strutturato
if data:
    doc.add_paragraph()
    self._add_bilancio_discussion(doc, data)
```

### Soluzione 3: Inserimento Intelligente
Trovare la posizione di "ORDINE DEL GIORNO" nel testo e inserire i punti subito dopo:

```python
# Trova la posizione di "ORDINE DEL GIORNO" e inserisci i punti
for i, section in enumerate(sections):
    if 'ORDINE DEL GIORNO' in section.get('content', '').upper():
        # Inserisci i punti dell'ordine del giorno dopo questa sezione
        # ... logica di inserimento
```

## 🎯 Soluzione Raccomandata

**Soluzione 1** è la migliore perché:
- Mantiene la flessibilità per l'utente
- Rileva correttamente se i punti sono già presenti
- Non duplica contenuto se l'utente ha già inserito i punti

## 📋 Piano di Implementazione

1. **Modificare la logica di rilevamento** nel metodo `_create_document_from_text`
2. **Testare con il testo fornito dall'utente**
3. **Verificare che i punti dell'ordine del giorno vengano aggiunti**
4. **Assicurarsi che non ci siano duplicazioni**

## 🧪 Test Case

### Input (testo modificato dall'utente):
```
ACME S.r.l.
...
ORDINE DEL GIORNO

Assume la presidenza...
```

### Output Atteso:
```
ACME S.r.l.
...
ORDINE DEL GIORNO

Assume la presidenza...

DISCUSSIONE E DELIBERAZIONI SUI PUNTI ALL'ORDINE DEL GIORNO
1. Approvazione del bilancio d'esercizio al [data]
2. Destinazione del risultato d'esercizio
...