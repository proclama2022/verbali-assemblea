# Standardizzazione Dati Comuni - Verbali di Assemblea

## 📋 Panoramica

È stato implementato un sistema di standardizzazione per l'estrazione e il popolamento delle informazioni comuni a tutti i verbali di assemblea. Questo elimina la duplicazione di codice e garantisce coerenza nell'esperienza utente.

## 🔧 Implementazione

### Nuovo Modulo: `CommonDataHandler`

È stato creato il modulo `src/common_data_handler.py` che centralizza la gestione dei dati comuni:

#### **Dati Standardizzati:**
- ✅ **Dati Azienda**: denominazione, sede legale, codice fiscale, capitale sociale
- ✅ **Dati Assemblea**: date, orari, luogo, tipo assemblea, configurazioni
- ✅ **Partecipanti**: soci, amministratori, presidente, segretario
- ✅ **Configurazioni Standard**: audioconferenza, collegio sindacale, revisore, ecc.

#### **Metodi Principali:**

1. **`extract_and_populate_company_data()`**
   - Gestisce denominazione, sede legale, codice fiscale
   - Processamento standardizzato del capitale sociale (deliberato/sottoscritto/versato)

2. **`extract_and_populate_assembly_data()`**
   - Date e orari assemblea
   - Tipo assemblea, convocazione, esito votazione
   - Checkbox standard (audioconferenza, collegio sindacale, revisore, ecc.)

3. **`extract_and_populate_participants_data()`**
   - Tabella soci con colonne standardizzate
   - Tabella amministratori (con supporto per colonne estese)
   - Selezione dinamica presidente e segretario
   - **NUOVO**: Parametro `extended_admin_columns` per template avanzati

## 🆕 Funzionalità Avanzate

### Supporto Template Avanzati
Il `CommonDataHandler` ora supporta funzionalità avanzate per template complessi:

```python
# Template base (semplice)
participants_data = CommonDataHandler.extract_and_populate_participants_data(
    extracted_data, 
    unique_key_suffix="template_nome"
)

# Template avanzato (con colonne estese)
participants_data = CommonDataHandler.extract_and_populate_participants_data(
    extracted_data, 
    unique_key_suffix="template_completo",
    extended_admin_columns=True  # Abilita: assente_giustificato, cariche CDA
)
```

### Risoluzione Conflitti Chiavi
- ✅ **Problema risolto**: Eliminati conflitti di chiavi duplicate
- ✅ **Architettura migliorata**: Template specifici non duplicano più la gestione amministratori
- ✅ **Post-processing intelligente**: Configurazioni specifiche applicate dopo i dati standard

### Correzioni Interfaccia Utente
- ✅ **Rappresentante Legale**: Risolto problema anteprima per società con rappresentante legale
- ✅ **Guida Utente**: Aggiunte note informative per campi condizionali
- ✅ **Debug Avanzato**: Sistema di diagnostica per identificare problemi dati
- ✅ **Help Context**: Tooltip esplicativi per i campi complessi
- ✅ **Duplicazione Presidente**: Risolto problema di duplicazione del presidente nell'elenco CDA

## 🔄 Template Aggiornati

### Prima (Problemi):
- ❌ Ogni template aveva la sua logica di estrazione
- ❌ Gestione diversa del capitale sociale
- ❌ Tabelle soci con colonne diverse
- ❌ Duplicazione di codice per configurazioni base

### Dopo (Soluzioni):
- ✅ Logica centralizzata nel `CommonDataHandler`
- ✅ Gestione uniforme di tutti i dati base
- ✅ Interfaccia utente consistente
- ✅ Codice template più pulito e focalizzato sulle specifiche

## 📝 Template Modificati

### 1. `verbale_assemblea_template.py` (Approvazione Bilancio)
- Utilizza `CommonDataHandler` per dati base
- Mantiene configurazioni specifiche per approvazione bilancio
- Sezione dedicata "Destinazione del Risultato"

### 2. `verbale_assemblea_completo_template.py` (Completo)
- Utilizza `CommonDataHandler` per dati base
- Configurazioni avanzate per CDA vs AU
- Gestione collegio sindacale e altri partecipanti

### 3. `verbale_assemblea_irregolare_template.py` (Irregolare)
- Utilizza `CommonDataHandler` per dati base
- Configurazioni specifiche per assemblee irregolari
- Campi per percentuali di presenza e motivi di irregolarità

## 🎯 Benefici

### **Per l'Utente:**
- **Esperienza Coerente**: Stessi campi, stesso layout in tutti i verbali
- **Dati Precompilati**: Informazioni estratte popolano automaticamente tutti i template
- **Interfaccia Uniforme**: Tabelle e controlli standardizzati

### **Per lo Sviluppatore:**
- **Manutenzione Semplificata**: Modifiche ai dati base in un solo posto
- **Codice Più Pulito**: Template focalizzati su funzionalità specifiche
- **Estensibilità**: Facile aggiungere nuovi template utilizzando i dati standard

### **Per il Sistema:**
- **Validazione Centralizzata**: Controlli coerenti sui dati richiesti
- **Gestione Errori Uniforme**: Messaggi di errore standardizzati
- **Performance**: Ridotta duplicazione di logica

## 🔍 Dati Standardizzati Comuni

### **Informazioni Azienda:**
```python
- denominazione: str
- sede_legale: str
- codice_fiscale: str
- capitale_deliberato: str
- capitale_sottoscritto: str
- capitale_versato: str
```

### **Informazioni Assemblea:**
```python
- data_assemblea: date
- ora_inizio: str
- ora_fine: str
- luogo_assemblea: str
- tipo_assemblea: ["Ordinaria", "Straordinaria"]
- tipo_convocazione: ["regolarmente convocata", "totalitaria"]
- esito_votazione: ["approvato all'unanimità", "approvato a maggioranza", "respinto"]
```

### **Configurazioni Standard:**
```python
- audioconferenza: bool
- documenti_allegati: bool
- collegio_sindacale: bool
- revisore: bool
- nome_revisore: str (condizionale)
- voto_palese: bool
- lingua_straniera: bool
```

### **Partecipanti Standardizzati:**
```python
# Soci
- nome: str
- quota_percentuale: str
- quota_euro: str
- presente: bool
- tipo_partecipazione: ["Diretto", "Delegato"]
- delegato: str
- tipo_soggetto: ["Persona Fisica", "Società"]
- rappresentante_legale: str

# Amministratori
- nome: str
- carica: str
- presente: bool

# Selezioni
- presidente: str (selezione dinamica)
- segretario: str (selezione dinamica)
```

## 🚀 Utilizzo per Nuovi Template

Per creare un nuovo template che utilizza i dati standardizzati:

```python
from common_data_handler import CommonDataHandler

def get_form_fields(self, extracted_data: dict) -> dict:
    form_data = {}
    
    # Dati base standardizzati
    form_data.update(CommonDataHandler.extract_and_populate_company_data(extracted_data))
    form_data.update(CommonDataHandler.extract_and_populate_assembly_data(extracted_data))
    form_data.update(CommonDataHandler.extract_and_populate_participants_data(
        extracted_data, 
        unique_key_suffix="mio_template"
    ))
    
    # Aggiungere qui solo configurazioni specifiche del template
    st.subheader("Configurazioni Specifiche")
    form_data["campo_specifico"] = st.text_input("Campo specifico", "")
    
    return form_data
```

## ✅ Stato Attuale

- [x] Modulo `CommonDataHandler` creato
- [x] Template approvazione bilancio aggiornato
- [x] Template completo aggiornato  
- [x] Template irregolare aggiornato
- [x] Test di importazione completati
- [x] Documentazione creata

## 🔮 Prossimi Passi

1. **Test Completo**: Verificare tutti i template con dati reali
2. **Ottimizzazioni UI**: Migliorare ulteriormente l'esperienza utente
3. **Validazioni Avanzate**: Implementare controlli più sofisticati
4. **Nuovi Template**: Utilizzare il sistema per template aggiuntivi

---

**Risultato**: Ora tutti i verbali utilizzano la stessa logica per l'estrazione e il popolamento delle informazioni standard, garantendo coerenza e facilitando la manutenzione del sistema. 