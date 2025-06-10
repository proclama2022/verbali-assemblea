"""
Modulo per caricare tutti i template disponibili nel sistema.
Questo file deve essere importato nell'app principale per registrare i template.
"""

import os
import sys
import importlib
import traceback

def load_all_templates():
    """Carica tutti i template dalla cartella templates/"""
    templates_dir = "templates"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Cartella {templates_dir}/ non trovata")
        return []
    
    # Aggiungi la cartella templates al path
    if templates_dir not in sys.path:
        sys.path.append(templates_dir)
    
    # Trova tutti i file Python nella cartella templates
    template_files = [f for f in os.listdir(templates_dir) 
                     if f.endswith('.py') and f != '__init__.py']
    
    if not template_files:
        print(f"❌ Nessun file template (.py) trovato in {templates_dir}/")
        return []
    
    print(f"🔍 Trovati {len(template_files)} file template: {template_files}")
    
    loaded_templates = []
    
    for template_file in template_files:
        module_name = template_file[:-3]  # Rimuovi .py
        try:
            print(f"📥 Tentativo di caricare: {module_name}")
            
            # Rimuovi il modulo dalla cache se già presente
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Importa il modulo template
            module = importlib.import_module(module_name)
            loaded_templates.append(module_name)
            print(f"✅ Template caricato: {module_name}")
            
        except Exception as e:
            print(f"❌ Errore nel caricare template {module_name}: {e}")
            print(f"📋 Traceback: {traceback.format_exc()}")
    
    print(f"🎯 Totale template caricati: {len(loaded_templates)}")
    return loaded_templates

if __name__ == "__main__":
    # Test del caricamento template
    print("🚀 Caricamento template...")
    loaded = load_all_templates()
    print(f"📄 Template caricati: {loaded}")
    
    # Mostra template disponibili
    try:
        from document_templates import DocumentTemplateFactory
        available = DocumentTemplateFactory.get_available_templates()
        print(f"🎯 Template disponibili nel factory: {available}")
    except Exception as e:
        print(f"❌ Errore nel verificare template factory: {e}") 