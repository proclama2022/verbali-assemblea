import os
import sys
from templates.verbale_assemblea_nomina_revisore_template import VerbaleNominaRevisoreTemplate
from datetime import datetime, date

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Sample data for nomina revisore
data = {
    "denominazione": "Example S.r.l.",
    "sede_legale": "Via Roma 1, Milano",
    "capitale_sociale": "10.000,00",
    "codice_fiscale": "12345678901",
    "data_assemblea": date(2025, 6, 12),
    "ora_assemblea": "10:00",
    "presidente": "Mario Rossi",
    "segretario": "Luigi Bianchi",
    "ruolo_presidente": "Amministratore Unico",
    "tipo_assemblea": "regolarmente convocata",
    "modalita_partecipazione": True,
    "motivo_nomina": "sopravvenuta scadenza del Revisore in carica",
    "socio_proponente": "Giuseppe Verdi",
    "durata_incarico": "il triennio 2025-2028",
    "compenso_annuo": "1.500,00",
    "revisore_presente": False,
    "soci": [
        {"nome": "Giuseppe Verdi", "quota_valore": "5.000,00", "quota_percentuale": "50%", "presente": True},
        {"nome": "Anna Russo", "quota_valore": "5.000,00", "quota_percentuale": "50%", "presente": True}
    ],
    "amministratori": [
        {"nome": "Mario Rossi", "carica": "Amministratore Unico", "presente": True}
    ],
    "revisore_dati": {
        "nome": "Dott. Francesco Bianchi",
        "nato_a": "Roma",
        "nato_il": date(1975, 3, 15),
        "residente": "Milano, Via Dante 10",
        "codice_fiscale": "BNCFNC75C15H501Z",
        "albo_data_gu": date(2020, 1, 15),
        "albo_num_gu": "15",
        "albo_serie_gu": "3A"
    },
    "punti_ordine_giorno": [
        "nomina del revisore della società"
    ]
}

# Generate document
template = VerbaleNominaRevisoreTemplate()
doc = template.generate_document(data)

# Save output
output_path = os.path.join(current_dir, "output", "nomina_revisore_formatted.docx")
doc.save(output_path)

print(f"Document generated at: {output_path}")
