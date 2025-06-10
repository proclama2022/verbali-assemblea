# 🎯 Guida alla Selezione Manuale Multi-Documenti

## 📋 Panoramica

Il sistema è stato aggiornato per permettere l'**estrazione separata** delle informazioni da ogni documento e la **selezione manuale** di quali informazioni utilizzare nel verbale finale, invece della combinazione automatica.

## 🔄 Nuovo Flusso di Lavoro

### 1. **Caricamento Documenti** 📤
- Carica diversi documenti (PDF o TXT) nella tab "Estrazione Multi-Documenti"
- Il sistema supporta tutti i tipi di documento: visura, bilancio, statuto, riconoscimento, fatture, contratti, generici
- **Non c'è più limite** al numero di documenti (rimosso il limite di 3)

### 2. **Elaborazione Separata** 🔍
- Ogni documento viene processato **separatamente** secondo il suo tipo
- Il sistema estrae le informazioni specifiche per ogni documento
- Viene mostrata un'analisi della **completezza** per ogni documento rispetto al template selezionato

### 3. **Analisi Template** 🎯
- Il sistema analizza quali campi del template sono disponibili in ogni documento
- Mostra una **tabella riassuntiva** con:
  - Campi disponibili per documento
  - Campi mancanti per documento  
  - Percentuale di completezza
- Visualizza i **dettagli per documento** con elenco specifico dei campi

### 4. **Selezione Manuale** ✏️
- **Interfaccia organizzata per categorie**: Azienda, Governance, Soci, Assemblea, Bilancio, Documenti, Contratti
- Per ogni campo del template, puoi scegliere:
  - **📄 Valore da un documento specifico** (con anteprima)
  - **✏️ Inserimento manuale** (campo di testo libero)
  - **🚫 Non inserire** (lascia vuoto)

### 5. **Riepilogo e Conferma** 📊
- Visualizza un **riepilogo delle selezioni** con:
  - Numero di campi compilati vs vuoti
  - Percentuale di completamento
  - Lista dettagliata delle scelte
- Pulsante **"Conferma Selezione e Procedi"** per finalizzare

## 🆕 Nuove Funzionalità

### **Estrazione Template-Specifica**
```python
# Il sistema estrae solo i campi rilevanti per il template selezionato
template_extraction = processor.extract_template_fields_from_documents(template_type)
```

### **Categorizzazione Intelligente**
I campi sono organizzati in categorie logiche:
- **🏢 Azienda**: denominazione, sede_legale, codice_fiscale, partita_iva, capitale
- **👥 Governance**: amministratori, rappresentanti, cariche  
- **💰 Soci**: soci, socio, quota
- **📅 Assemblea**: data_assemblea, luogo_assemblea, ordine_giorno, presenti
- **💼 Bilancio**: patrimonio, risultato, ricavi, costi, utile, perdita, chiusura
- **📄 Documenti**: documento, riconoscimento, passaporto, carta_identita
- **📝 Contratti**: contratto, parte_a, parte_b, valore

### **Interfaccia di Selezione Avanzata**
- **Radio buttons** per scegliere la fonte di ogni campo
- **Anteprima JSON** per dati complessi (liste, oggetti)
- **Input manuale** per correzioni o aggiunte
- **Persistenza delle selezioni** durante la sessione

### **Analisi di Completezza**
- **Percentuale di completezza** per ogni documento
- **Tabella riassuntiva** con metriche chiare
- **Dettaglio campi** disponibili/mancanti per documento

## 🎮 Come Usare il Sistema

### **Passo 1: Preparazione**
1. Seleziona e blocca il **template** nella sidebar
2. Vai alla tab **"Estrazione Multi-Documenti"**

### **Passo 2: Caricamento**
1. Carica i tuoi documenti (PDF o TXT)
2. Per ogni documento:
   - Il sistema **suggerisce automaticamente** il tipo
   - Puoi modificare il tipo se necessario
   - Clicca **"Elabora"** per processare

### **Passo 3: Analisi**
1. Visualizza la **tabella di analisi** dei campi template
2. Espandi **"Dettaglio Campi per Documento"** per vedere i dettagli
3. Controlla la **completezza** di ogni documento

### **Passo 4: Selezione**
1. Scorri l'**interfaccia di selezione** organizzata per categorie
2. Per ogni campo:
   - Scegli la **fonte** (documento specifico, manuale, o vuoto)
   - Visualizza l'**anteprima** se necessario
   - Inserisci **valori manuali** se richiesto

### **Passo 5: Finalizzazione**
1. Controlla il **riepilogo** delle selezioni
2. Verifica la **percentuale di completamento**
3. Clicca **"Conferma Selezione e Procedi"**
4. Vai alla tab **"Genera Documento"** per creare il verbale

## 🔧 Vantaggi del Nuovo Sistema

### **✅ Controllo Totale**
- **Tu decidi** quale informazione usare per ogni campo
- **Nessuna combinazione automatica** che potrebbe essere errata
- **Trasparenza completa** su cosa viene inserito nel documento

### **✅ Flessibilità**
- **Correzioni manuali** per qualsiasi campo
- **Combinazione** di informazioni da documenti diversi
- **Campi vuoti** se l'informazione non è disponibile

### **✅ Organizzazione**
- **Categorizzazione logica** dei campi
- **Interfaccia intuitiva** con icone e descrizioni
- **Riepilogo chiaro** delle scelte effettuate

### **✅ Efficienza**
- **Analisi automatica** della completezza
- **Suggerimenti automatici** per i tipi di documento
- **Persistenza** delle selezioni durante la sessione

## 🚨 Differenze dal Sistema Precedente

| **Prima** | **Ora** |
|-----------|---------|
| Combinazione automatica | Selezione manuale |
| Risoluzione conflitti AI | Scelta diretta dell'utente |
| Limite 3 documenti | Nessun limite |
| Analisi conflitti | Analisi completezza |
| Processo opaco | Controllo trasparente |

## 🎯 Casi d'Uso Tipici

### **Scenario 1: Documenti Complementari**
- **Visura**: dati aziendali e soci
- **Bilancio**: dati finanziari
- **Documento ID**: dati personali amministratore
- **Risultato**: Selezioni diverse fonti per campi diversi

### **Scenario 2: Documenti con Conflitti**
- **Visura vecchia**: denominazione "ABC SRL"
- **Contratto nuovo**: denominazione "ABC S.R.L."
- **Risultato**: Scegli manualmente quale versione usare

### **Scenario 3: Informazioni Incomplete**
- **Bilancio**: solo dati finanziari
- **Risultato**: Inserisci manualmente i dati mancanti o lasciali vuoti

## 🔍 Risoluzione Problemi

### **Problema: Campo non trovato in nessun documento**
- **Soluzione**: Usa l'opzione **"✏️ Inserisci manualmente"**

### **Problema: Informazione presente ma formato sbagliato**
- **Soluzione**: Seleziona il documento e poi **correggi manualmente**

### **Problema: Troppi campi vuoti**
- **Soluzione**: Carica **documenti aggiuntivi** o **inserisci manualmente**

### **Problema: Selezioni perse**
- **Soluzione**: Le selezioni sono **salvate automaticamente** nella sessione

## 🎉 Conclusione

Il nuovo sistema di **selezione manuale** ti dà il **controllo completo** su quali informazioni utilizzare nel verbale finale, eliminando gli errori della combinazione automatica e garantendo **precisione** e **trasparenza** nel processo. 