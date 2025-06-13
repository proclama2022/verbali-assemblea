import os
import sys
from templates.verbale_assemblea_completo_template import VerbaleAssembleaCompletoTemplate
from datetime import datetime, date

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Sample data
data = {
    "denominazione": "Example S.r.l.",
    "sede_legale": "Via Roma 1, Milano",
    "capitale_sociale": "10.000,00",
    "codice_fiscale": "12345678901",
    "data_assemblea": date(2025, 6, 12),
    "ora_assemblea": "10:00",
    "presidente": "Mario Rossi",
    "segretario": "Luigi Bianchi",
    "soci": [
        {"nome": "Giuseppe Verdi", "quota_euro": "5.000,00", "quota_percentuale": "50%", "presente": True},
        {"nome": "Anna Russo", "quota_euro": "5.000,00", "quota_percentuale": "50%", "presente": True}
    ],
    "amministratori": [
        {"nome": "Mario Rossi", "carica": "Amministratore Unico", "presente": True}
    ],
    "tipo_amministrazione": "Amministratore Unico",
    "data_chiusura": date(2024, 12, 31),
    "punti_ordine_giorno": [
        "Approvazione bilancio 2024",
        "Nomina revisore dei conti"
    ]
}

# Generate document
template = VerbaleAssembleaCompletoTemplate()
doc = template.generate_document(data)

# Save output
output_path = os.path.join(current_dir, "output", "formatted_verbale.docx")
doc.save(output_path)

print(f"Document generated at: {output_path}")
