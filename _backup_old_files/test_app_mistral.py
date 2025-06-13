#!/usr/bin/env python3
import os
import time
from dotenv import load_dotenv
from mistralai import Mistral
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Carica le variabili d'ambiente come fa l'app
load_dotenv()
api_key = os.environ.get("MISTRAL_API_KEY")

print(f"🔑 API Key caricata: {api_key[:10]}...{api_key[-5:] if api_key else 'NONE'}")

if not api_key:
    print("❌ MISTRAL_API_KEY non trovata nel file .env")
    exit(1)

# Inizializza il client Mistral come fa l'app
try:
    client = Mistral(api_key=api_key)
    print("✅ Client Mistral inizializzato correttamente")
except Exception as e:
    print(f"❌ Errore inizializzazione client: {e}")
    exit(1)

# Test della chiamata esatta che fa l'app
test_text = "Questo è un testo di test per l'estrazione di informazioni."
prompt = f"""Estrai le seguenti informazioni dal testo fornito e restituiscile in formato JSON:

{{
    "tipo_documento": "tipo di documento identificato",
    "contenuto_principale": "riassunto del contenuto"
}}

Testo da analizzare:
{test_text}"""

messages = [{"role": "user", "content": prompt}]

def make_api_call():
    return client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        temperature=0
    )

print("\n🧪 Test chiamata API con ThreadPoolExecutor (come nell'app)...")

max_retries = 3
for attempt in range(max_retries):
    try:
        if attempt > 0:
            print(f"🔄 Tentativo {attempt + 1} di {max_retries}...")
        
        # Usa ThreadPoolExecutor con timeout di 30 secondi (come nell'app)
        with ThreadPoolExecutor() as executor:
            future = executor.submit(make_api_call)
            start_time = time.time()
            
            print(f"⏳ Chiamata API in corso... (timeout: 30s)")
            chat_response = future.result(timeout=30)
            
            elapsed_time = time.time() - start_time
            print(f"✅ Risposta ricevuta in {elapsed_time:.2f} secondi")
            
            response_text = chat_response.choices[0].message.content
            print(f"📝 Risposta: {response_text[:200]}...")
            
            # Successo - esci dal loop
            break
            
    except FutureTimeoutError:
        elapsed = time.time() - start_time
        print(f"⏰ TIMEOUT al tentativo {attempt + 1} dopo {elapsed:.1f} secondi")
        if attempt == max_retries - 1:
            print("❌ Tutti i tentativi falliti per timeout")
        else:
            print("⏸️ Pausa 2 secondi prima del prossimo tentativo...")
            time.sleep(2)
            
    except Exception as e:
        print(f"❌ Errore al tentativo {attempt + 1}: {e}")
        if attempt == max_retries - 1:
            print("❌ Tutti i tentativi falliti")
        else:
            time.sleep(2)

print("\n🏁 Test completato")