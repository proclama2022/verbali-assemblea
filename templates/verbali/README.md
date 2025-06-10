# Template Verbali Assemblea

Questa cartella contiene i template disponibili per la generazione di verbali di assemblea dei soci.

## Template Disponibili

### 1. **Approvazione Bilancio** (`verbale_assemblea_template.py`)
- **Scopo**: Verbali per l'approvazione del bilancio di esercizio
- **Caratteristiche**: 
  - Gestione destinazione risultato (riserva legale, dividendi, riporto a nuovo)
  - Campi specifici per dati contabili
  - Calcolo automatico percentuali destinazione

### 2. **Verbale Completo** (`verbale_assemblea_completo_template.py`)
- **Scopo**: Verbali generici per assemblee complete
- **Caratteristiche**: 
  - Struttura completa e flessibile
  - Gestione di diverse tipologie di delibere
  - Supporto per assemblee miste (presenza + audioconferenza)

### 3. **Assemblea Irregolare** (`verbale_assemblea_irregolare_template.py`)
- **Scopo**: Verbali per assemblee con irregolarità procedurali
- **Caratteristiche**: 
  - Gestione note su irregolarità
  - Disclaimer legali
  - Validazione speciale per assemblee non conformi

### 4. **Correzioni/Precisazioni** (`verbale_assemblea_correzioni_template.py`)
- **Scopo**: Verbali per correggere/precisare verbali precedenti
- **Caratteristiche**: 
  - Riferimento al verbale da correggere
  - Gestione multipla correzioni (testo errato → testo corretto)
  - Supporto traduzioni per partecipanti stranieri
  - Ordine del giorno specifico per precisazioni
  - Gestione errori materiali e integrazioni

### 5. **Distribuzione Dividendi** (`verbale_assemblea_dividendi_template.py`) ⭐ NUOVO
- **Scopo**: Verbali per la distribuzione di dividendi ai soci
- **Caratteristiche**: 
  - Calcolo automatico dividendi per socio
  - Gestione modalità di ripartizione (proporzionale, da atto costitutivo)
  - Prelievo da riserve disponibili
  - Gestione votazioni (unanimità, maggioranza, astensioni)
  - Relazione finanziaria e proposta di distribuzione

## Struttura Comune

Tutti i template seguono questa struttura standardizzata:

1. **Header Aziendale**: Denominazione, sede, capitale sociale, codice fiscale
2. **Titolo e Data**: Verbale di assemblea dei soci del [data]
3. **Apertura**: Luogo, ora, ordine del giorno
4. **Partecipanti**: Presidente, segretario, soci presenti/rappresentati
5. **Dichiarazioni Preliminari**: Validità assemblea, audioconferenza
6. **Svolgimento**: Contenuto specifico del template
7. **Chiusura**: Approvazione verbale, ora di scioglimento
8. **Firme**: Presidente e segretario

## Utilizzo del Nuovo Template Correzioni

Il template per correzioni/precisazioni è ideale quando:

- Si deve correggere un errore materiale in un verbale precedente
- Si devono aggiungere precisazioni a delibere già approvate  
- Si devono integrare informazioni mancanti

### Campi Specifici del Template Correzioni:

- **Data verbale precedente**: Data dell'assemblea da correggere
- **Tipo correzione**: Errore materiale/Precisazione/Integrazione
- **Correzioni multiple**: Possibilità di specificare più correzioni
- **Delibera precedente**: Descrizione di cosa fu deliberato in precedenza
- **Traduzione**: Supporto per partecipanti che non parlano italiano

### Esempio di Utilizzo:

```
Data verbale precedente: 15/03/2024
Correzione 1: 
  - Testo errato: "capitale sociale €10.000"
  - Testo corretto: "capitale sociale €50.000"
  
Delibera precedente: "ha deliberato l'approvazione del bilancio"
```

## Utilizzo del Nuovo Template Dividendi

Il template per distribuzione dividendi è ideale quando:

- Si devono distribuire utili ai soci
- Si vogliono prelevare fondi da riserve disponibili
- È necessario calcolare automaticamente i dividendi per quota

### Campi Specifici del Template Dividendi:

- **Importo totale dividendi**: Somma complessiva da distribuire
- **Socio proponente**: Chi propone la distribuzione
- **Tipo distribuzione**: Utili pregressi/Riserve/Utile esercizio
- **Modalità ripartizione**: Proporzionale o personalizzata
- **Calcolo automatico**: Dividendi per socio basati su percentuali
- **Modalità voto**: Unanimità, maggioranza con contrari/astenuti

### Esempio di Utilizzo:

```
Importo dividendi: €50.000,00
Socio proponente: Mario Rossi
Tipo distribuzione: Utili pregressi
Modalità ripartizione: Proporzionale alla quota

Calcolo automatico:
- Socio A (60%): €30.000,00
- Socio B (40%): €20.000,00
```

## Note Tecniche

- Tutti i template utilizzano `CommonDataHandler` per standardizzare i dati
- Il sistema carica automaticamente tutti i template dalla cartella `templates/`
- I template sono registrati tramite `DocumentTemplateFactory`
- Supporto completo per Streamlit UI con anteprima dinamica

## Base di Estrazione

⚠️ **IMPORTANTE**: La base di estrazione deve rimanere identica per tutti i template. 

- I campi comuni (denominazione, sede, capitale sociale, etc.) vengono estratti automaticamente
- Solo i campi specifici del template vengono aggiunti
- Non devono esserci opzioni nel file finale - devono essere specificate dall'utente prima della generazione

## Mantenimento

Per aggiungere un nuovo template:
1. Creare un nuovo file `.py` nella cartella `templates/`
2. Estendere la classe `DocumentTemplate`
3. Implementare i metodi richiesti
4. Registrare il template con `DocumentTemplateFactory.register_template()`
5. Il sistema caricherà automaticamente il nuovo template 