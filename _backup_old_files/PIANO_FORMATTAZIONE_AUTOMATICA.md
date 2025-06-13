# Piano di Implementazione - Formattazione Automatica Documenti Word

## Obiettivo
Implementare un sistema di riconoscimento automatico della struttura del testo per generare documenti Word con formattazione professionale, mantenendo la possibilità per l'utente di modificare il contenuto nell'anteprima.

## Analisi del Problema Attuale
- Il metodo `_create_document_from_text()` converte tutto in testo semplice
- Gli stili professionali esistenti non vengono applicati al testo modificato dall'utente
- Perdita della formattazione quando l'utente modifica l'anteprima

## Soluzione: Sistema di Riconoscimento Automatico

### 1. Pattern di Riconoscimento

#### Intestazioni Aziendali
```
PATTERN: Testo in maiuscolo all'inizio del documento
ESEMPIO: "PARTITAIVA.IT S.R.L."
STILE: CompanyHeader (centrato, grassetto, 12pt)
```

#### Titoli Principali
```
PATTERN: "VERBALE DI ASSEMBLEA" o testo tutto maiuscolo centrato
ESEMPIO: "VERBALE DI ASSEMBLEA DEI SOCI"
STILE: VerbaleTitle (centrato, grassetto, 16pt, maiuscolo)
```

#### Sottotitoli
```
PATTERN: Testo tra parentesi o date
ESEMPIO: "(ORDINARIA)" o "del 04/06/2025"
STILE: VerbaleSubtitle (centrato, grassetto, 12pt)
```

#### Intestazioni di Sezione
```
PATTERN: Testo tutto maiuscolo, spesso preceduto da spazio
ESEMPIO: "ORDINE DEL GIORNO", "SOCI PRESENTI E RAPPRESENTATI"
STILE: SectionHeader (centrato, grassetto, 14pt, maiuscolo)
```

#### Elenchi Puntati
```
PATTERN: Righe che iniziano con "•", "-", "*" o "- "
ESEMPIO: "• PROCLAMA S.T.P. SPA (società - legale rappresentante: Nino Billa)"
STILE: List Bullet (rientrato, punto elenco)
```

#### Elenchi Numerati
```
PATTERN: Righe che iniziano con numeri seguiti da punto o parentesi
ESEMPIO: "1. Approvazione del Bilancio di esercizio"
STILE: List Number (rientrato, numerato)
```

#### Testo Normale
```
PATTERN: Tutto il resto
STILE: BodyText (giustificato, 12pt, Times New Roman)
```

### 2. Algoritmo di Riconoscimento

```python
def _analyze_text_structure(self, text: str) -> List[Dict]:
    """
    Analizza il testo e restituisce una lista di sezioni con i loro stili
    """
    sections = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            sections.append({'type': 'empty', 'content': '', 'style': None})
            continue
            
        # 1. Intestazione aziendale (prime righe, maiuscolo)
        if i < 5 and line.isupper() and len(line) > 10:
            sections.append({'type': 'company_header', 'content': line, 'style': 'CompanyHeader'})
            
        # 2. Titolo principale verbale
        elif 'VERBALE' in line.upper() and 'ASSEMBLEA' in line.upper():
            sections.append({'type': 'main_title', 'content': line, 'style': 'VerbaleTitle'})
            
        # 3. Sottotitoli (parentesi o date)
        elif (line.startswith('(') and line.endswith(')')) or 'del ' in line:
            sections.append({'type': 'subtitle', 'content': line, 'style': 'VerbaleSubtitle'})
            
        # 4. Intestazioni di sezione (maiuscolo, parole chiave)
        elif (line.isupper() and any(keyword in line for keyword in 
              ['ORDINE', 'SOCI', 'AMMINISTRATORI', 'PUNTO', 'DELIBERA'])):
            sections.append({'type': 'section_header', 'content': line, 'style': 'SectionHeader'})
            
        # 5. Elenchi puntati
        elif line.startswith(('•', '-', '*', '- ')):
            sections.append({'type': 'bullet_list', 'content': line, 'style': 'List Bullet'})
            
        # 6. Elenchi numerati
        elif re.match(r'^\d+[\.\)]\s', line):
            sections.append({'type': 'numbered_list', 'content': line, 'style': 'List Number'})
            
        # 7. Testo normale
        else:
            sections.append({'type': 'body_text', 'content': line, 'style': 'BodyText'})
    
    return sections
```

### 3. Implementazione nel Template

#### Nuovo Metodo `_create_formatted_document_from_text()`
- Sostituisce `_create_document_from_text()`
- Analizza la struttura del testo
- Applica gli stili appropriati
- Mantiene la formattazione professionale

#### Miglioramenti agli Stili Esistenti
- Aggiunta di stili per separatori (`---`)
- Miglioramento degli elenchi puntati
- Gestione delle tabelle semplici

### 4. Vantaggi della Soluzione

✅ **Formattazione Automatica**: Riconosce automaticamente la struttura
✅ **Flessibilità**: L'utente può modificare il testo nell'anteprima
✅ **Professionalità**: Mantiene l'aspetto professionale del documento
✅ **Compatibilità**: Funziona con il sistema esistente
✅ **Robustezza**: Fallback a testo normale se il riconoscimento fallisce

### 5. Test Cases

#### Input di Test
```
PARTITAIVA.IT S.R.L.
Sede legale: TORINO (TO) CORSO FERRUCCI, 112 EDIFICIO 1 CAP 10138

VERBALE DI ASSEMBLEA DEI SOCI
(ORDINARIA)
del 04/06/2025

ORDINE DEL GIORNO
1. Approvazione del Bilancio di esercizio chiuso al 31/12/2024

SOCI PRESENTI E RAPPRESENTATI
• PROCLAMA S.T.P. SPA (società - legale rappresentante: Nino Billa) - quota 10% pari a Euro 1.000,00
• ELAPSO S.R.L. (socio) - quota 40% pari a Euro 4.000,00
```

#### Output Atteso
- "PARTITAIVA.IT S.R.L." → CompanyHeader (centrato, grassetto)
- "Sede legale..." → CompanyHeader (centrato, normale)
- "VERBALE DI ASSEMBLEA DEI SOCI" → VerbaleTitle (centrato, grassetto, maiuscolo)
- "(ORDINARIA)" → VerbaleSubtitle (centrato, grassetto)
- "del 04/06/2025" → VerbaleSubtitle (centrato, grassetto)
- "ORDINE DEL GIORNO" → SectionHeader (centrato, grassetto, maiuscolo)
- "1. Approvazione..." → List Number (numerato)
- "SOCI PRESENTI..." → SectionHeader (centrato, grassetto, maiuscolo)
- "• PROCLAMA..." → List Bullet (puntato)

## Implementazione

Il nuovo sistema sarà implementato nel file `templates/verbale_assemblea_template.py` sostituendo il metodo `_create_document_from_text()` con una versione avanzata che riconosce automaticamente la struttura del testo.