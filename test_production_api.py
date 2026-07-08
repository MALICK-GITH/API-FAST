"""
Script de test de l'API de production sur Render
================================================

Author: SOLITAIRE HACK
Version: 1.0
"""

import requests
import json

# URL de production
BASE_URL = "https://api-fast-qnvg.onrender.com"

def test_health():
    """Teste l'endpoint /health"""
    print("=" * 80)
    print("TEST DE L'ENDPOINT /HEALTH")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_predict():
    """Teste l'endpoint /predict"""
    print("\n" + "=" * 80)
    print("TEST DE L'ENDPOINT /PREDICT")
    print("=" * 80)
    
    payload = {
        "I": "734915710",
        "O1": "Barcelone",
        "O2": "Galatasaray",
        "L": "FC 26. 5x5 Rush. Superligue",
        "S": 1783516200,
        "E": [
            {"T": 1, "C": 1.096},
            {"T": 2, "C": 6.14},
            {"T": 3, "C": 30}
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_leagues():
    """Teste l'endpoint /leagues"""
    print("\n" + "=" * 80)
    print("TEST DE L'ENDPOINT /LEAGUES")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/leagues")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("\n" + "=" * 80)
    print("TEST DE L'API DE PRODUCTION - RENDER")
    print("=" * 80)
    print(f"URL: {BASE_URL}")
    print("=" * 80)
    
    results = {
        "health": test_health(),
        "predict": test_predict(),
        "leagues": test_leagues()
    }
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    for endpoint, success in results.items():
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{endpoint.upper()}: {status}")
    
    all_success = all(results.values())
    print("=" * 80)
    if all_success:
        print("✅ TOUS LES TESTS RÉUSSIS - API DE PRODUCTION OPÉRATIONNELLE")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("=" * 80)

if __name__ == "__main__":
    main()
