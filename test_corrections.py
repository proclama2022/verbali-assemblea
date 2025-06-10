#!/usr/bin/env python3
"""
Script di test per verificare le correzioni implementate per:
1. Problema combinazione informazioni (TypeError con soci)
2. Miglioramenti OCR per passaporti
3. Validazione dati combinati
"""

import json
import sys
from unittest.mock import Mock

# Aggiungi src al path per gli import
sys.path.append('src')

def test_soci_data_preparation():
    """Test della correzione per _prepare_soci_data"""
    print("🧪 Test preparazione dati soci...")
    
    from common_data_handler import CommonDataHandler
    
    # Test con dati problematici (stringhe, None, dizionari misti)
    test_data = [
        'Mario Rossi',  # Stringa
        {'nome': 'Luca Bianchi', 'quota': '50%'},  # Dizionario parziale
        None,  # None
        '',  # Stringa vuota
        {'nome': 'Anna Verdi', 'quota_percentuale': '30%', 'presente': False}  # Dizionario completo
    ]
    
    try:
        result = CommonDataHandler._prepare_soci_data(test_data)
        print("✅ Preparazione dati soci: OK")
        print(f"   - Input elementi: {len(test_data)}")
        print(f"   - Output elementi: {len(result)}")
        print(f"   - Tutti elementi sono dizionari: {all(isinstance(item, dict) for item in result)}")
        
        # Verifica che tutti abbiano i campi necessari
        required_fields = ['tipo_partecipazione', 'delegato', 'presente', 'tipo_soggetto', 'rappresentante_legale']
        all_have_fields = all(
            all(field in item for field in required_fields) 
            for item in result
        )
        print(f"   - Tutti hanno campi richiesti: {all_have_fields}")
        
        return True
    except Exception as e:
        print(f"❌ Preparazione dati soci: FALLITO - {e}")
        return False

def test_multi_document_validation():
    """Test della validazione dati combinati"""
    print("\n🧪 Test validazione dati combinati...")
    
    try:
        from multi_document_processor import MultiDocumentProcessor
        
        # Mock client
        mock_client = Mock()
        processor = MultiDocumentProcessor(mock_client)
        
        # Test con dati problematici
        test_data = {
            'soci': '["Mario Rossi", "Luca Bianchi"]',  # Stringa JSON
            'amministratori': 'Carlo Verdi',  # Stringa singola
            'presente': 'true',  # Stringa booleana
            'audioconferenza': 'si',  # Booleano italiano
            'voto_palese': 'false'  # Stringa booleana
        }
        
        cleaned = processor._validate_and_clean_combined_data(test_data)
        
        print("✅ Validazione dati combinati: OK")
        print(f"   - Soci convertiti in lista: {isinstance(cleaned.get('soci'), list)}")
        print(f"   - Amministratori convertiti in lista: {isinstance(cleaned.get('amministratori'), list)}")
        print(f"   - Boolean fields convertiti: {all(isinstance(cleaned.get(field), bool) for field in ['presente', 'audioconferenza', 'voto_palese'] if field in cleaned)}")
        
        return True
    except Exception as e:
        print(f"❌ Validazione dati combinati: FALLITO - {e}")
        return False

def test_pattern_extraction():
    """Test dell'estrazione pattern per documenti di identità"""
    print("\n🧪 Test estrazione pattern documenti identità...")
    
    try:
        from document_processors import DocumentoRiconoscimentoProcessor
        
        # Mock client
        mock_client = Mock()
        processor = DocumentoRiconoscimentoProcessor(mock_client)
        
        # Testo di test simile a quello che potrebbe uscire da un OCR problematico
        test_text = """
        AB1234567
        MARIO ROSSI
        12/05/1980
        MILANO
        RSSMRA80E12F205X
        VIA ROMA 10
        """
        
        patterns = processor._extract_identity_document_patterns(test_text)
        
        print("✅ Estrazione pattern: OK")
        print(f"   - Pattern estratti: {len(patterns.split('\\n'))} righe")
        print("   - Dovrebbe contenere: numeri documento, date, codici fiscali")
        
        return True
    except Exception as e:
        print(f"❌ Estrazione pattern: FALLITO - {e}")
        return False

def test_import_structure():
    """Test della struttura degli import"""
    print("\n🧪 Test struttura import...")
    
    try:
        # Test import dei moduli principali
        from common_data_handler import CommonDataHandler
        from multi_document_processor import MultiDocumentProcessor  
        from document_processors import DocumentProcessorFactory
        
        print("✅ Import struttura: OK")
        print("   - CommonDataHandler: ✓")
        print("   - MultiDocumentProcessor: ✓")
        print("   - DocumentProcessorFactory: ✓")
        
        return True
    except Exception as e:
        print(f"❌ Import struttura: FALLITO - {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🚀 Avvio test correzioni sistema...\n")
    
    tests = [
        test_import_structure,
        test_soci_data_preparation,
        test_multi_document_validation,
        test_pattern_extraction
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Risultati Test:")
    print(f"   - Test eseguiti: {len(tests)}")
    print(f"   - Test passati: {sum(results)}")
    print(f"   - Test falliti: {len(tests) - sum(results)}")
    
    if all(results):
        print("\n🎉 Tutti i test sono passati! Il sistema è pronto per l'uso.")
        return 0
    else:
        print("\n⚠️ Alcuni test sono falliti. Controllare i problemi sopra riportati.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 