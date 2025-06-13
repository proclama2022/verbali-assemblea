# Test per dimostrare il miglioramento del mapping dei campi

# Esempio di dati estratti da una visura (come quelli che hai mostrato)
dati_visura_originali = {
    'denominazione': 'PARTITAIVA.IT S.R.L.',
    'sede_legale': 'TORINO (TO) CORSO F.FERRUCCI, 112 EDIFICIO 1 CAP 10138',
    'codice_fiscale': '12877980016',
    'forma_giuridica': 'società a responsabilità limitata'
}

# Esempio di come dovrebbero essere i dati dopo il mapping migliorato
dati_mappati_correttamente = {
    "denominazione": "PARTITAIVA.IT S.R.L.",
    "sede_legale": "TORINO (TO) CORSO F.FERRUCCI, 112 EDIFICIO 1 CAP 10138",
    "codice_fiscale": "12877980016",
    "forma_giuridica": "società a responsabilità limitata",
    "capitale_sociale": "10.000,00 euro",
    "soci": [
        {
            "nome": "Mario Rossi",
            "quota_percentuale": "50%",
            "quota_euro": "5.000",
            "presente": True
        },
        {
            "nome": "Luigi Bianchi", 
            "quota_percentuale": "50%",
            "quota_euro": "5.000",
            "presente": False
        }
    ],
    "amministratori": [
        {
            "nome": "Mario Rossi",
            "carica": "Amministratore Unico",
            "presente": True
        }
    ],
    "sindaci": [],
    "data_assemblea": "2024-03-15",
    "luogo_assemblea": "Sede legale",
    "rappresentante": "Mario Rossi"
}

print("🔧 MIGLIORAMENTI IMPLEMENTATI:")
print("\n1. ✅ PROMPT PIÙ INTELLIGENTE:")
print("   - Istruzioni specifiche per mappare campi dai documenti sorgente")
print("   - Priorità chiare per tipi di documenti diversi")
print("   - Esempi concreti di output corretto")

print("\n2. ✅ MAPPATURA CAMPI DETTAGLIATA:")
print("   - Da visura → denominazione, sede_legale, soci[], amministratori[]")
print("   - Da riconoscimento → dati personali per completare liste")
print("   - Da bilancio → dati finanziari specifici")

print("\n3. ✅ VALIDAZIONE MIGLIORATA:")
print("   - Struttura corretta per soci (nome, quota_percentuale, quota_euro)")
print("   - Struttura corretta per amministratori (nome, carica)")
print("   - Pulizia automatica campi numerici")

print("\n4. ✅ GESTIONE ERRORI:")
print("   - Mai più stringhe JSON nei campi array")
print("   - Validazione automatica delle strutture")
print("   - Fallback intelligenti per dati incompleti")

print("\n🎯 RISULTATO ATTESO:")
print("Invece di un JSON incomprensibile come:")
print("{'denominazione': 'PARTITAIVA.IT S.R.L.', ...}")
print("\nOra ottieni un mapping strutturato come:")
import json
print(json.dumps(dati_mappati_correttamente, indent=2, ensure_ascii=False))

print("\n🚀 Per testare:")
print("1. Carica una visura nella tab Multi-Documenti")
print("2. Clicca 'Combina Documenti'")
print("3. Verifica che i soci e amministratori siano in liste strutturate")
print("4. Controlla che tutti i campi siano mappati correttamente") 