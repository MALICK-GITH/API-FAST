"""
Test API de Production - Nouvelle URL
=====================================

Teste l'API de production avec la nouvelle URL:
https://api-fast-82wa.onrender.com

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import requests
import json

PRODUCTION_URL = "https://api-fast-82wa.onrender.com"

print("=" * 80)
print("TEST API DE PRODUCTION - NOUVELLE URL")
print("=" * 80)
print(f"URL: {PRODUCTION_URL}")
print()

# Test 1: Health Check
print("=" * 80)
print("TEST 1: HEALTH CHECK")
print("=" * 80)
try:
    response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
    if response.status_code == 200:
        print("✅ Health check réussi")
        print(f"   Réponse: {response.json()}")
    else:
        print(f"❌ Health check échoué - Status Code: {response.status_code}")
        print(f"   Réponse: {response.text}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()

# Test 2: Ligues disponibles
print("=" * 80)
print("TEST 2: LIGUES DISPONIBLES")
print("=" * 80)
try:
    response = requests.get(f"{PRODUCTION_URL}/leagues", timeout=10)
    if response.status_code == 200:
        leagues = response.json()
        print(f"✅ Ligues disponibles: {leagues.get('total', 0)}")
        print(f"   Premières ligues:")
        for league in leagues.get('leagues', [])[:5]:
            print(f"   - {league}")
    else:
        print(f"❌ Erreur ligues - Status Code: {response.status_code}")
        print(f"   Réponse: {response.text}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()

# Test 3: Prédiction single match
print("=" * 80)
print("TEST 3: PRÉDICTION SINGLE MATCH")
print("=" * 80)
try:
    payload = {
        "I": "match_test_001",
        "O1": "Barcelone",
        "O2": "Galatasaray",
        "L": "FC 26. 5x5 Rush. Superligue",
        "S": 1783516200,
        "SC": None,
        "E": [
            {"T": 1, "C": 1.096, "P": None, "B": "888starz", "G": 1},
            {"T": 2, "C": 6.14, "P": None, "B": "888starz", "G": 1},
            {"T": 3, "C": 30, "P": None, "B": "888starz", "G": 1}
        ],
        "AE": [
            {
                "G": 2,
                "ME": [
                    {"T": 7, "C": 1.95, "P": -1.0, "B": "888starz"},
                    {"T": 8, "C": 1.95, "P": 1.0, "B": "888starz"}
                ]
            }
        ]
    }
    
    response = requests.post(
        f"{PRODUCTION_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Prédiction réussie")
        print(f"   Match: {result.get('team_home')} vs {result.get('team_away')}")
        print(f"   Ligue: {result.get('league')}")
        print(f"   Prédiction: {result.get('predictions', {}).get('match_result', {}).get('prediction')}")
        print(f"   Total Goals: {result.get('predictions', {}).get('total_goals', {}).get('predicted')}")
        print(f"   Parity: {result.get('predictions', {}).get('total_parity', {}).get('prediction')}")
    else:
        print(f"❌ Prédiction échouée - Status Code: {response.status_code}")
        print(f"   Réponse: {response.text}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()

# Test 4: Batch prediction
print("=" * 80)
print("TEST 4: BATCH PREDICTION")
print("=" * 80)
try:
    batch_payload = {
        "matches": [
            {
                "I": "match_test_001",
                "O1": "Barcelone",
                "O2": "Galatasaray",
                "L": "FC 26. 5x5 Rush. Superligue",
                "S": 1783516200,
                "SC": None,
                "E": [],
                "AE": []
            },
            {
                "I": "match_test_002",
                "O1": "Arsenal",
                "O2": "Lille OSC",
                "L": "FC 25. Champions League",
                "S": 1783516200,
                "SC": None,
                "E": [],
                "AE": []
            }
        ]
    }
    
    response = requests.post(
        f"{PRODUCTION_URL}/predict/batch",
        json=batch_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Batch prediction réussie")
        print(f"   Total matchs: {result.get('total')}")
        print(f"   Prédictions: {len(result.get('predictions', []))}")
        for i, pred in enumerate(result.get('predictions', [])):
            print(f"   Match {i+1}: {pred.get('team_home')} vs {pred.get('team_away')} - {pred.get('predictions', {}).get('match_result', {}).get('prediction')}")
    else:
        print(f"❌ Batch prediction échouée - Status Code: {response.status_code}")
        print(f"   Réponse: {response.text}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()
print("=" * 80)
print("✅ TESTS TERMINÉS")
print("=" * 80)
