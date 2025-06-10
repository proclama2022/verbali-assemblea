# 🔍 Sistema di Risoluzione Conflitti Intelligente

## Panoramica

Il sistema implementa una risoluzione conflitti avanzata che utilizza **Mistral AI** per analizzare automaticamente le discrepanze tra documenti e presenta opzioni intuitive all'utente per la risoluzione.

## 🚀 Funzionalità Principali

### 1. **Analisi AI Automatica**
- Rileva conflitti tra documenti usando pattern recognition intelligente
- Assegna livelli di confidenza (ALTO, MEDIO, BASSO)
- Fornisce raccomandazioni basate su contesto e tipologia documento

### 2. **UI Interattiva per Risoluzione**
- Presenta visualmente le opzioni conflittuali
- Mostra la fonte di ogni informazione (visura, documento riconoscimento, etc.)
- Permette inserimento valori personalizzati
- Traccia la provenienza delle decisioni

### 3. **Integrazione Seamless**
- Si attiva automaticamente durante la combinazione multi-documenti
- Mantiene le decisioni dell'utente per l'intera sessione
- Applica risoluzioni in modo coerente nella generazione finale

## 📋 Tipi di Conflitti Rilevati

### Conflitti di Valore Diverso
```
Esempio: Nome in visura = "MARIO ROSSI SRL" 
         Nome in documento = "Mario Rossi S.r.l."
```

### Conflitti di Formato
```
Esempio: Data in fattura = "15/03/2024"
         Data in contratto = "2024-03-15"
```

### Valori Mancanti
```
Esempio: Codice fiscale presente solo in un documento
```

## 🎯 Flusso di Utilizzo

### Passo 1: Caricamento Multi-Documenti
1. Vai alla tab "Multi-Documenti"
2. Carica almeno 2 documenti di tipi diversi
3. Il sistema processerà automaticamente ogni documento

### Passo 2: Anteprima Conflitti (Opzionale)
```
🔍 Anteprima Analisi Conflitti
├── 🤖 Analizza Conflitti [Button]
├── ⚠️ Lista conflitti potenziali
├── 💡 Raccomandazioni AI
└── 📊 Riassunto analisi
```

### Passo 3: Combinazione con Risoluzione
1. Seleziona template target
2. Clicca "🔗 Combina Documenti"
3. **Se ci sono conflitti, apparirà l'interfaccia di risoluzione**

### Passo 4: Risoluzione Conflitti Interattiva
```
🔴 Conflitto 1: denominazione (ALTO)
├── 📋 Opzioni disponibili:
│   ├── 📄 visura.pdf (visura): "MARIO ROSSI SRL"
│   ├── 📄 documento.pdf (riconoscimento): "Mario Rossi S.r.l."
│   ├── ✏️ Inserisci valore personalizzato
│   └── ❌ Lascia vuoto (salta questo campo)
├── 🤖 Raccomandazione AI: "Usa il formato dalla visura..."
└── 🎯 Confidence: 🏢 visura, 🆔 riconoscimento
```

## 🧠 Logica AI di Analisi

### Campi Prioritari Controllati
- **Denominazione/Nome** azienda o persona
- **Codice Fiscale/Partita IVA**
- **Indirizzi e sedi legali**
- **Date** (nascita, costituzione, etc.)
- **Numeri di documento**
- **Importi e valori numerici**
- **Nomi di persone** (amministratori, soci, etc.)

### Livelli di Confidenza
- **🔴 ALTO**: Conflitti evidenti che richiedono attenzione
- **🟡 MEDIO**: Discrepanze probabili ma non certe
- **🟢 BASSO**: Differenze minori di formato o capitalizzazione

### Raccomandazioni AI
L'AI considera:
- **Tipologia documento** (visura = più affidabile per dati aziendali)
- **Completezza informazione** (preferisce campi più dettagliati)
- **Coerenza formale** (formati standard vs varianti)
- **Contesto temporale** (documenti più recenti)

## 🎨 Elementi UI

### Icone per Tipologie Documenti
- 🏢 **Visura** (Camera di Commercio)
- 🆔 **Riconoscimento** (Carta identità, passaporto)
- 💰 **Bilancio** (Documenti finanziari)
- 🧾 **Fattura** (Documenti commerciali)
- 📝 **Contratto** (Accordi legali)

### Indicatori di Stato
- ✅ **Risolto** - Conflitto risolto dall'utente
- ⚠️ **Pendente** - Richiede attenzione utente
- 🤖 **AI Suggerisce** - Raccomandazione disponibile
- 📊 **Riassunto** - Overview generale

## 🔧 Implementazione Tecnica

### Nuovi Metodi in MultiDocumentProcessor

```python
# Analisi conflitti con AI
analyze_conflicts_with_ai() -> Dict[str, Any]

# UI interattiva per risoluzione
display_conflict_resolution_ui(conflicts_analysis) -> Dict[str, Any]

# Combinazione con risoluzioni applicate
combine_documents_with_conflict_resolution(template) -> Dict[str, Any]
```

### Formato Dati Conflitti
```json
{
  "conflicts": [
    {
      "field_name": "denominazione",
      "conflict_type": "VALORE_DIVERSO",
      "confidence_level": "ALTO",
      "description": "Diversi formati dello stesso nome",
      "values": [
        {
          "value": "MARIO ROSSI SRL",
          "source_document": "visura.pdf",
          "document_type": "visura",
          "confidence": "Formato ufficiale da registro imprese"
        }
      ],
      "ai_recommendation": "Usa il formato dalla visura per coerenza legale"
    }
  ],
  "summary": "Rilevati 3 conflitti, principalmente di formato"
}
```

## 🎯 Benefici

### Per l'Utente
- **Trasparenza totale** su fonte di ogni informazione
- **Controllo completo** delle decisioni finali
- **Guidance intelligente** da parte dell'AI
- **Processo intuitivo** con UI chiara

### Per la Qualità Dati
- **Riduzione errori** attraverso validazione incrociata
- **Coerenza garantita** nel documento finale
- **Tracciabilità** delle decisioni prese
- **Automazione intelligente** dei casi ovvi

## 🔮 Possibili Estensioni Future

1. **Machine Learning** per apprendere dalle scelte utente
2. **Regole business** personalizzabili per settore
3. **Integrazione database** per validazione esterna
4. **API esterne** per verifica codici fiscali/partite IVA
5. **Workflow approval** per team di lavoro

## 📖 Esempi Pratici

### Scenario: Visura + Documento Identità
```
Conflitto rilevato:
- Visura: "MARIO ROSSI" (amministratore)
- Doc. Identità: "Mario Giuseppe Rossi"

AI suggerisce: "Usa nome completo dal documento identità 
per accuratezza anagrafica"

Utente sceglie: "Mario Giuseppe Rossi"
Risultato: Nome completo nel verbale finale
```

### Scenario: Date in Formati Diversi
```
Conflitto rilevato:
- Fattura: "15/03/2024"  
- Contratto: "2024-03-15"

AI suggerisce: "Entrambe rappresentano la stessa data,
usa formato italiano standard"

Utente sceglie: "15/03/2024"
Risultato: Formato coerente nel documento
```

Questo sistema trasforma la gestione multi-documenti da un processo propenso agli errori in un workflow intelligente e guidato dall'AI, mantenendo sempre il controllo finale all'utente. 