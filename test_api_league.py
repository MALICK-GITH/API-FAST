"""
Test de l'API par Ligues
========================
Script pour tester l'API avec les nouveaux modèles par ligues

Author: SOLITAIRE HACK
Version: 1.0
"""

import requests
import json

print("=== TEST DE L'API PAR LIGUES ===\n")

base_url = "http://localhost:5000"

# Test 1: Health check
print("1. Test du health check...")
try:
    response = requests.get(f"{base_url}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   Erreur: {e}")

# Test 2: Liste des ligues
print("\n2. Test de la liste des ligues...")
try:
    response = requests.get(f"{base_url}/leagues")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total ligues: {data['total']}")
    print(f"   Ligues:")
    for league in data['leagues'][:5]:
        print(f"     - {league['name']}")
except Exception as e:
    print(f"   Erreur: {e}")

# Test 3: Prédiction simple
print("\n3. Test de prédiction simple...")
test_match = {
    "I": "734797802",
    "O1": "Club Atlético de Madrid",
    "O2": "Porto",
    "L": "FC 26. 5x5 Rush. Superligue",
    "S": 1783473000,
    "ST": "Paris avant le début du jeu"
}

try:
    response = requests.post(f"{base_url}/predict", json=test_match)
    print(f"   Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"   Match: {data['team_home']} vs {data['team_away']}")
        print(f"   Ligue: {data['league']}")
        print(f"   Famille: {data['family']}")
        print(f"   Résultat: {data['predictions']['match_result']['prediction']} (conf: {data['predictions']['match_result']['confidence']:.2f})")
        print(f"   Total Buts: {data['predictions']['total_goals']['predicted']:.1f}")
        print(f"   Parité: {data['predictions']['total_parity']['prediction']}")
        print(f"   Over/Under: {data['predictions']['over_under']['prediction']} ({data['predictions']['over_under']['threshold']})")
    else:
        print(f"   Erreur: {data.get('error')}")
except Exception as e:
    print(f"   Erreur: {e}")

# Test 4: Prédiction batch
print("\n4. Test de prédiction batch...")
test_matches = [
    {
        "I": "734797802",
        "O1": "Club Atlético de Madrid",
        "O2": "Porto",
        "L": "FC 26. 5x5 Rush. Superligue"
    },
    {
        "I": "734796647",
        "O1": "Galatasaray",
        "O2": "Bayer 04",
        "L": "FC 26. 5x5 Rush. Superligue"
    }
]

try:
    response = requests.post(f"{base_url}/predict/batch", json={"matches": test_matches})
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total: {data['total']}")
    for pred in data['predictions']:
        if pred.get('success'):
            print(f"   - {pred['team_home']} vs {pred['team_away']}: {pred['predictions']['match_result']['prediction']}")
        else:
            print(f"   - Erreur: {pred.get('error')}")
except Exception as e:
    print(f"   Erreur: {e}")

# Test 5: Info modèle
print("\n5. Test d'info modèle...")
try:
    response = requests.get(f"{base_url}/model/FC 26. 5x5 Rush. Superligue")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   Erreur: {e}")

print("\n=== TEST TERMINÉ ===")
