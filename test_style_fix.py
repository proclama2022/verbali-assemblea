#!/usr/bin/env python3
"""
Test script per verificare che il fix degli stili funzioni correttamente
"""

import sys
import os
from datetime import datetime

# Aggiungi i path necessari
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
templates_path = os.path.join(current_dir, 'templates')

if src_path not in sys.path:
    sys.path.append(src_path)
if templates_path not in sys.path:
    sys.path.append(templates_path)

def test_amministratore_unico_generation():
    """Test della generazione del verbale amministratore unico"""
    try:
        from templates.verbale_assemblea_amministratore_unico_template import VerbaleAmministratoreUnicoTemplate
        
        # Dati di test
        test_data = {
            'denominazione': 'TEST SRL',
            'sede_legale': 'Via Roma 1, Milano (MI)',
            'capitale_sociale': '10.000,00',
            'codice_fiscale': '12345678901',
            'data_assemblea': datetime(2024, 1, 15),
            'ora_assemblea': datetime.strptime('10:00', '%H:%M').time(),
            'presidente': 'Mario Rossi',
            'segretario': 'Luigi Bianchi',
            'soci': [
                {
                    'nome': 'Mario Rossi',
                    'quota_euro': '5000',
                    'quota_percentuale': '50',
                    'tipo_soggetto': 'Persona Fisica',
                    'tipo_partecipazione': 'Diretta',
                    'presente': True
                },
                {
                    'nome': 'Luigi Bianchi', 
                    'quota_euro': '5000',
                    'quota_percentuale': '50',
                    'tipo_soggetto': 'Persona Fisica',
                    'tipo_partecipazione': 'Diretta',
                    'presente': True
                }
            ],
            'amministratore_unico': {
                'nome': 'Mario Rossi',
                'data_nascita': datetime(1980, 1, 1),
                'luogo_nascita': 'Milano (MI)',
                'codice_fiscale': 'RSSMRA80A01F205X',
                'residenza': 'Via Roma 1, Milano (MI)',
                'qualifica': 'Socio'
            },
            'include_compensi': True,
            'compenso_annuo': '1.000,00'
        }
        
        # Crea il template
        template = VerbaleAmministratoreUnicoTemplate()
        
        print("🔧 Testing document generation...")
        
        # Genera il documento
        doc = template.generate_document(test_data)
        
        # Salva il documento di test
        output_path = os.path.join(current_dir, 'output', 'test_amministratore_unico_fixed.docx')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        
        print(f"✅ Document generated successfully!")
        print(f"📄 Saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_template_styles():
    """Test della creazione degli stili tramite il template concreto"""
    try:
        from templates.verbale_assemblea_amministratore_unico_template import VerbaleAmministratoreUnicoTemplate
        from docx import Document
        
        print("🔧 Testing base template style creation via concrete template...")
        
        # Crea un documento vuoto
        doc = Document()
        
        # Crea un'istanza del template concreto
        template = VerbaleAmministratoreUnicoTemplate()
        
        # Testa la configurazione degli stili
        template._setup_document_styles(doc)
        
        # Verifica che gli stili siano stati creati o che il fallback funzioni
        styles = doc.styles
        style_names = [s.name for s in styles]
        
        print(f"📋 Available styles: {style_names}")
        
        # Testa l'aggiunta dell'header aziendale
        test_data = {
            'denominazione': 'TEST SRL',
            'sede_legale': 'Via Roma 1, Milano (MI)',
            'capitale_sociale': '10.000,00',
            'codice_fiscale': '12345678901'
        }
        
        template._add_company_header(doc, test_data)
        
        # Salva il documento di test
        output_path = os.path.join(current_dir, 'output', 'test_base_template_styles.docx')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        
        print(f"✅ Base template test successful!")
        print(f"📄 Saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in base template test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting style fix tests...")
    print("=" * 50)
    
    # Test 1: Base template styles
    print("\n1️⃣ Testing base template style creation...")
    base_test_result = test_base_template_styles()
    
    # Test 2: Full document generation
    print("\n2️⃣ Testing full document generation...")
    full_test_result = test_amministratore_unico_generation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Base template styles: {'✅ PASS' if base_test_result else '❌ FAIL'}")
    print(f"   Full document generation: {'✅ PASS' if full_test_result else '❌ FAIL'}")
    
    if base_test_result and full_test_result:
        print("\n🎉 All tests passed! The style fix is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        sys.exit(1)
