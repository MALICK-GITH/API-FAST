"""
Script de démarrage complet du système FIFA Prediction
========================================================
Ce script démarre l'API et traite automatiquement les données live

Author: SOLITAIRE HACK
Version: 1.0
"""

import subprocess
import time
import os
import signal
import sys
from threading import Thread

def start_api():
    """Démarre l'API Flask"""
    print("=" * 80)
    print("DÉMARRAGE DE L'API FIFA PREDICTION")
    print("=" * 80)
    print("URL: http://localhost:5000")
    print("URL Production: https://api-fast-qnvg.onrender.com")
    print("=" * 80)
    
    process = subprocess.Popen(
        [sys.executable, "prediction_api_league.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Attendre que l'API démarre
    time.sleep(5)
    
    return process

def process_live_data():
    """Traite les données live de la plateforme"""
    print("\n" + "=" * 80)
    print("TRAITEMENT DES DONNÉES LIVE")
    print("=" * 80)
    
    if not os.path.exists("live_data_input.json"):
        print("⚠️  Fichier live_data_input.json non trouvé")
        print("   Création d'un fichier d'exemple...")
        
        example_data = {
            "Value": [
                {
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
            ]
        }
        
        import json
        with open("live_data_input.json", "w", encoding="utf-8") as f:
            json.dump(example_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Fichier live_data_input.json créé avec des données d'exemple")
    
    process = subprocess.Popen(
        [sys.executable, "process_full_live_data.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        print("✅ Traitement des données live terminé avec succès")
        print(stdout)
    else:
        print("❌ Erreur lors du traitement des données live")
        print(stderr)

def main():
    """Fonction principale"""
    print("\n" + "=" * 80)
    print("SYSTÈME FIFA PREDICTION - DÉMARRAGE COMPLET")
    print("=" * 80)
    print("Author: SOLITAIRE HACK")
    print("Version: 1.0")
    print("=" * 80)
    
    try:
        # Démarrer l'API
        api_process = start_api()
        
        # Traiter les données live
        process_live_data()
        
        print("\n" + "=" * 80)
        print("SYSTÈME EN MARCHE")
        print("=" * 80)
        print("✅ API démarrée sur http://localhost:5000")
        print("✅ Données live traitées")
        print("✅ Rapport sauvegardé dans live_predictions_report.json")
        print("=" * 80)
        print("\nAppuyez sur Ctrl+C pour arrêter le système")
        print("Le système continue de fonctionner en arrière-plan...")
        print("=" * 80)
        
        # Garder l'API en marche
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\n\nArrêt du système...")
            api_process.terminate()
            api_process.wait()
            print("✅ Système arrêté")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
