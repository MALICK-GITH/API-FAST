"""
Test Manuel de l'API - FURY X ONE
================================

Ce script teste l'API avec les nouveaux modèles FURY X ONE
en démarrant l'API manuellement.

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import requests
import json
import time

print("=" * 80)
print("TEST MANUEL DE L'API - FURY X ONE")
print("=" * 80)
print("\n⚠️  IMPORTANT: L'API doit être démarrée manuellement")
print("   Commande: python prediction_api_league.py")
print("   Ensuite appuyez sur ENTER pour continuer...")
input()

try:
    # Test 1: Health check
    print("\n" + "=" * 80)
    print("TEST 1: HEALTH CHECK")
    print("=" * 80)
    
    response = requests.get("http://localhost:5000/health")
    if response.status_code == 200:
        print("✅ Health check réussi")
        print(f"   Status: {response.json()}")
    else:
        print(f"❌ Health check échoué - Status Code: {response.status_code}")
    
    # Test 2: Ligues disponibles
    print("\n" + "=" * 80)
    print("TEST 2: LIGUES DISPONIBLES")
    print("=" * 80)
    
    response = requests.get("http://localhost:5000/leagues")
    if response.status_code == 200:
        leagues = response.json()
        print(f"✅ Ligues disponibles: {len(leagues.get('leagues', []))}")
        for league in leagues.get('leagues', [])[:5]:
            print(f"   - {league}")
    else:
        print(f"❌ Erreur ligues - Status Code: {response.status_code}")
    
    # Test 3: Prédiction avec format plateforme
    print("\n" + "=" * 80)
    print("TEST 3: PRÉDICTION FORMAT PLATEFORME")
    print("=" * 80)
    
    platform_payload = {
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
        "http://localhost:5000/predict",
        json=platform_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Test de prédiction réussi")
        print(f"   Match: {result.get('team_home')} vs {result.get('team_away')}")
        print(f"   Ligue: {result.get('league')}")
        print(f"   Prédiction: {result.get('predictions', {}).get('match_result', {}).get('prediction')}")
        print(f"   Total Goals: {result.get('predictions', {}).get('total_goals', {}).get('predicted')}")
        print(f"   Parity: {result.get('predictions', {}).get('total_parity', {}).get('prediction')}")
    else:
        print(f"❌ Test de prédiction échoué - Status Code: {response.status_code}")
        print(response.text)
    
    # Test 4: Batch prediction
    print("\n" + "=" * 80)
    print("TEST 4: BATCH PREDICTION")
    print("=" * 80)
    
    batch_payload = {
        "matches": [
            {
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
            },
            {
                "I": "match_test_002",
                "O1": "Arsenal",
                "O2": "Lille OSC",
                "L": "FC 25. Champions League",
                "S": 1783516200,
                "SC": None,
                "E": [
                    {"T": 1, "C": 1.85, "P": None, "B": "888starz", "G": 1},
                    {"T": 2, "C": 3.20, "P": None, "B": "888starz", "G": 1},
                    {"T": 3, "C": 4.50, "P": None, "B": "888starz", "G": 1}
                ],
                "AE": []
            }
        ]
    }
    
    response = requests.post(
        "http://localhost:5000/predict/batch",
        json=batch_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Test de batch prediction réussi")
        print(f"   Total matchs: {result.get('total')}")
        print(f"   Prédictions: {len(result.get('predictions', []))}")
        for i, pred in enumerate(result.get('predictions', [])):
            print(f"   Match {i+1}: {pred.get('team_home')} vs {pred.get('team_away')} - {pred.get('predictions', {}).get('match_result', {}).get('prediction')}")
    else:
        print(f"❌ Test de batch prediction échoué - Status Code: {response.status_code}")
        print(response.text)
    
    print("\n" + "=" * 80)
    print("✅ TESTS TERMINÉS AVEC SUCCÈS")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Erreur lors des tests: {e}")
    print("   Assurez-vous que l'API est démarrée avec: python prediction_api_league.py")
