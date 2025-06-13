#!/usr/bin/env python3
"""
Test per verificare che tutti i template ereditino correttamente da BaseVerbaleTemplate
"""

import sys
import os

# Aggiungi i path necessari
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
templates_path = os.path.join(current_dir, 'templates')

if src_path not in sys.path:
    sys.path.append(src_path)
if templates_path not in sys.path:
    sys.path.append(templates_path)

def test_base_template_import():
    """Test import del BaseVerbaleTemplate"""
    try:
        from base_verbale_template import BaseVerbaleTemplate
        print("✓ BaseVerbaleTemplate importato correttamente")
        return True
    except Exception as e:
        print(f"✗ Errore nell'importazione di BaseVerbaleTemplate: {e}")
        return False

def test_template_inheritance():
    """Test che tutti i template ereditino da BaseVerbaleTemplate"""
    templates_to_test = [
        ('verbale_assemblea_template', 'VerbaleApprovazioneBilancioTemplate'),
        ('verbale_assemblea_dividendi_template', 'VerbaleDividendiTemplate'),
        ('verbale_assemblea_completo_template', 'VerbaleAssembleaCompletoTemplate'),
        ('verbale_assemblea_nomina_revisore_template', 'VerbaleNominaRevisoreTemplate'),
        ('verbale_assemblea_generico_template', 'VerbaleAssembleaGenericoTemplate'),
        ('verbale_assemblea_amministratore_unico_template', 'VerbaleAmministratoreUnicoTemplate'),
    ]
    
    success_count = 0
    total_count = len(templates_to_test)
    
    for module_name, class_name in templates_to_test:
        try:
            module = __import__(module_name)
            template_class = getattr(module, class_name)
            
            # Verifica che erediti da BaseVerbaleTemplate
            from base_verbale_template import BaseVerbaleTemplate
            if issubclass(template_class, BaseVerbaleTemplate):
                print(f"✓ {class_name} eredita correttamente da BaseVerbaleTemplate")
                success_count += 1
            else:
                print(f"✗ {class_name} NON eredita da BaseVerbaleTemplate")
                
        except Exception as e:
            print(f"✗ Errore nel test di {class_name}: {e}")
    
    print(f"\nRisultato: {success_count}/{total_count} template testati con successo")
    return success_count == total_count

if __name__ == "__main__":
    print("=== Test Integrazione BaseVerbaleTemplate ===")
    print()
    
    # Test import base
    base_ok = test_base_template_import()
    print()
    
    if base_ok:
        # Test ereditarietà
        inheritance_ok = test_template_inheritance()
        print()
        
        if inheritance_ok:
            print("🎉 Tutti i test sono passati! I template ora ereditano correttamente da BaseVerbaleTemplate")
        else:
            print("⚠️  Alcuni template hanno problemi di ereditarietà")
    else:
        print("❌ Impossibile procedere: BaseVerbaleTemplate non può essere importato")