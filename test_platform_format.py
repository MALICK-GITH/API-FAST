"""
Test de l'API avec le format de la plateforme
==============================================

Ce script teste l'API avec le format de données envoyé par la plateforme.

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import requests
import json

# URL de l'API locale
BASE_URL = "http://localhost:5000"

def test_platform_format():
    """Teste l'API avec le format de la plateforme"""
    
    print("=" * 80)
    print("TEST DE L'API AVEC LE FORMAT DE LA PLATEFORME")
    print("=" * 80)
    
    # Payload au format de la plateforme
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
    
    print("\n📊 PAYLOAD ENVOYÉ (Format Plateforme):")
    print(json.dumps(platform_payload, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=platform_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 STATUS CODE: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n📊 RÉPONSE DE L'API:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                print("\n✅ TEST RÉUSSI - L'API accepte le format de la plateforme")
                return True
            else:
                print(f"\n❌ TEST ÉCHOUÉ - Erreur: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"\n❌ TEST ÉCHOUÉ - Status Code: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False

def test_league_mapping():
    """Teste le mapping de noms de ligues"""
    
    print("\n" + "=" * 80)
    print("TEST DU MAPPING DE LIGUES")
    print("=" * 80)
    
    test_cases = [
        {"L": "Ligue 1", "expected": "FC 25. Championnat d'Angleterre"},
        {"L": "Champions League", "expected": "FC 26. Champions League"},
        {"L": "FC 26. 5x5 Rush. Superligue", "expected": "FC 26. 5x5 Rush. Superligue"},
    ]
    
    for test in test_cases:
        payload = {
            "I": "test",
            "O1": "Team1",
            "O2": "Team2",
            "L": test["L"],
            "S": 1783516200
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/predict",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                actual_league = result.get('league', '')
                expected = test["expected"]
                
                if actual_league == expected:
                    print(f"✅ {test['L']} -> {actual_league}")
                else:
                    print(f"⚠️  {test['L']} -> {actual_league} (attendu: {expected})")
            else:
                print(f"❌ {test['L']} - Erreur API")
                
        except Exception as e:
            print(f"❌ {test['L']} - Erreur: {e}")

if __name__ == "__main__":
    success = test_platform_format()
    test_league_mapping()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ L'API EST COMPATIBLE AVEC LE FORMAT DE LA PLATEFORME")
    else:
        print("❌ L'API N'EST PAS COMPATIBLE - CORRECTIONS NÉCESSAIRES")
    print("=" * 80)
