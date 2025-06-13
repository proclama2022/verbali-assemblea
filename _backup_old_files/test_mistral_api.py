#!/usr/bin/env python3
import os
import requests
import json
import time

# Test dell'API Mistral
api_key = "n3df0Odcsj36VF3RaELJEjAOWak4Uq0m"
url = "https://api.mistral.ai/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "mistral-tiny",
    "messages": [
        {"role": "user", "content": "Ciao, questo è un test"}
    ],
    "max_tokens": 50
}

print("🔍 Test connessione API Mistral...")
print(f"URL: {url}")
print(f"API Key: {api_key[:10]}...{api_key[-5:]}")

try:
    start_time = time.time()
    response = requests.post(url, headers=headers, json=data, timeout=30)
    elapsed_time = time.time() - start_time
    
    print(f"⏱️ Tempo di risposta: {elapsed_time:.2f} secondi")
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API funziona correttamente!")
        print(f"📝 Risposta: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
    else:
        print(f"❌ Errore API: {response.status_code}")
        print(f"📄 Risposta: {response.text}")
        
except requests.exceptions.Timeout:
    print("⏰ TIMEOUT: L'API non risponde entro 30 secondi")
except requests.exceptions.ConnectionError:
    print("🌐 ERRORE CONNESSIONE: Impossibile raggiungere l'API")
except Exception as e:
    print(f"❌ ERRORE GENERICO: {str(e)}")