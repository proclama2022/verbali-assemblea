#!/usr/bin/env python3
"""
Test per il template di Revoca dell'Amministratore Unico e nomina di nuovo Organo Amministrativo
"""

import sys
import os

# Aggiungi i path necessari
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from load_templates import load_all_templates
from document_templates import DocumentTemplateFactory

def test_revoca_nomina_template():
    """Test del template di revoca e nomina"""
    
    print("🚀 Test template Revoca e Nomina...")
    
    # Carica i template
    loaded = load_all_templates()
    print(f"📄 Template caricati: {len(loaded)}")
    
    # Verifica che il template sia disponibile
    available_templates = DocumentTemplateFactory.get_available_templates()
    print(f"🎯 Template disponibili: {available_templates}")
    
    # Verifica che il nostro template sia presente
    template_key = 'verbale_assemblea_revoca_nomina'
    if template_key in available_templates:
        print(f"✅ Template '{template_key}' trovato!")
        
        try:
            # Crea un'istanza del template
            template = DocumentTemplateFactory.create_template(template_key)
            print(f"✅ Template istanziato: {template.get_template_name()}")
            
            # Verifica i campi richiesti
            required_fields = template.get_required_fields()
            print(f"📋 Campi richiesti: {required_fields}")
            
            # Test con dati di esempio
            test_data = {
                'denominazione': 'TEST SRL',
                'sede_legale': 'Via Test 1, Roma',
                'capitale_sociale': '10.000,00',
                'codice_fiscale': 'TSTSTR12L34M456N',
                'data_assemblea': '2024-01-15',
                'ora_assemblea': '14:30',
                'presidente': 'Mario Rossi',
                'segretario': 'Luigi Bianchi',
                'soci': [],
                'amministratore_revocato': {
                    'nome': 'Giovanni Verdi',
                    'inadempimenti': 'Test inadempimenti'
                },
                'nuovo_amministratore': {
                    'nome': 'Paolo Neri',
                    'qualifica': 'Socio',
                    'durata_incarico': 'A tempo indeterminato',
                    'compenso': '15.000,00'
                }
            }
            
            # Test generazione preview
            print("🔍 Test generazione anteprima...")
            preview = template._generate_preview_text(test_data)
            print(f"✅ Anteprima generata (lunghezza: {len(preview)} caratteri)")
            
            print("✅ Tutti i test sono passati!")
            return True
            
        except Exception as e:
            print(f"❌ Errore nel test del template: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"❌ Template '{template_key}' NON trovato nei template disponibili!")
        return False

if __name__ == "__main__":
    success = test_revoca_nomina_template()
    print(f"\n🎯 Test {'PASSATO' if success else 'FALLITO'}!") 