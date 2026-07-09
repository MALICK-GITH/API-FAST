"""
Script Complet de Test et Commit - FURY X ONE
=============================================

Ce script effectue:
1. Test de l'API avec les nouveaux modèles
2. Commit des changements
3. Push vers GitHub

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import subprocess
import sys
import time

print("=" * 80)
print("TEST ET COMMIT - FURY X ONE")
print("=" * 80)

# ÉTAPE 1: Démarrer l'API
print("\n" + "=" * 80)
print("ÉTAPE 1: DÉMARRAGE DE L'API")
print("=" * 80)

api_process = subprocess.Popen(
    [sys.executable, "prediction_api_league.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print("✅ API démarrée en arrière-plan")
time.sleep(10)  # Attendre que l'API démarre (augmenté à 10 secondes)

# ÉTAPE 2: Tester l'API
print("\n" + "=" * 80)
print("ÉTAPE 2: TEST DE L'API")
print("=" * 80)

try:
    import requests
    
    # Test avec le format de la plateforme
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
        print("✅ Test de l'API réussi")
        print(f"   Match: {result.get('team_home')} vs {result.get('team_away')}")
        print(f"   Ligue: {result.get('league')}")
        print(f"   Prédiction: {result.get('predictions', {}).get('match_result', {}).get('prediction')}")
        print(f"   Total Goals: {result.get('predictions', {}).get('total_goals', {}).get('predicted')}")
    else:
        print(f"❌ Test de l'API échoué - Status Code: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")

# Arrêter l'API
api_process.terminate()
api_process.wait()
print("\n✅ API arrêtée")

# ÉTAPE 3: Commit des changements
print("\n" + "=" * 80)
print("ÉTAPE 3: COMMIT DES CHANGEMENTS")
print("=" * 80)

try:
    # Ajouter tous les fichiers
    subprocess.run(["git", "add", "."], check=True)
    print("✅ Fichiers ajoutés")
    
    # Commit
    commit_message = "Mise à jour FURY X ONE - Nouveaux modèles entraînés avec 36019 matchs"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    print("✅ Commit créé")
    
    # Push
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Push vers GitHub réussi")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors du commit/push: {e}")

print("\n" + "=" * 80)
print("✅ PROCESSUS TERMINÉ")
print("=" * 80)
