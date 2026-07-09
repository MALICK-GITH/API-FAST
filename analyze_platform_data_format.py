"""
Analyse du format de données envoyé par la plateforme
======================================================

Ce script analyse les différences entre le format envoyé par la plateforme
et le format attendu par notre API FIFA Prediction.

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import json
from typing import Dict, Any, List

def analyze_platform_format():
    """Analyse le format envoyé par la plateforme"""
    
    print("=" * 80)
    print("ANALYSE DU FORMAT DE DONNÉES ENVOYÉ PAR LA PLATEFORME")
    print("=" * 80)
    
    # Format envoyé par la plateforme (selon la documentation)
    platform_payload = {
        "I": "match_12345",
        "O1": "Paris Saint-Germain",
        "O2": "Olympique Lyonnais",
        "L": "Ligue 1",
        "S": 1719504000,
        "SC": None,
        "E": [
            {
                "T": 1,
                "C": 1.85,
                "P": None,
                "B": "888starz",
                "G": 1
            },
            {
                "T": 2,
                "C": 3.40,
                "P": None,
                "B": "888starz",
                "G": 1
            },
            {
                "T": 3,
                "C": 4.20,
                "P": None,
                "B": "888starz",
                "G": 1
            },
            {
                "T": 9,
                "C": 1.90,
                "P": 2.5,
                "B": "888starz",
                "G": 17
            },
            {
                "T": 10,
                "C": 1.90,
                "P": 2.5,
                "B": "888starz",
                "G": 17
            }
        ],
        "AE": [
            {
                "G": 2,
                "ME": [
                    {
                        "T": 7,
                        "C": 1.95,
                        "P": -1.0,
                        "B": "888starz"
                    },
                    {
                        "T": 8,
                        "C": 1.95,
                        "P": 1.0,
                        "B": "888starz"
                    }
                ]
            }
        ]
    }
    
    # Format attendu par notre API actuelle
    api_expected = {
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
    
    print("\n📊 FORMAT ENVOYÉ PAR LA PLATEFORME:")
    print(json.dumps(platform_payload, indent=2, ensure_ascii=False))
    
    print("\n📊 FORMAT ATTENDU PAR NOTRE API:")
    print(json.dumps(api_expected, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("DIFFÉRENCES IDENTIFIÉES")
    print("=" * 80)
    
    differences = []
    
    # 1. Champ SC (Score)
    if "SC" in platform_payload and "SC" not in api_expected:
        differences.append({
            "type": "CHAMP SUPPLÉMENTAIRE",
            "field": "SC",
            "description": "La plateforme envoie le score actuel (SC) que notre API n'attend pas",
            "impact": "FAIBLE - Ce champ est optionnel et peut être ignoré"
        })
    
    # 2. Champs B et G dans les marchés
    if "E" in platform_payload and platform_payload["E"]:
        first_market = platform_payload["E"][0]
        if "B" in first_market:
            differences.append({
                "type": "CHAMP SUPPLÉMENTAIRE DANS MARCHÉ",
                "field": "E[].B",
                "description": "La plateforme inclut le bookmaker (B) dans chaque marché",
                "impact": "FAIBLE - Ce champ est optionnel et peut être ignoré"
            })
        if "G" in first_market:
            differences.append({
                "type": "CHAMP SUPPLÉMENTAIRE DANS MARCHÉ",
                "field": "E[].G",
                "description": "La plateforme inclut le groupe de marché (G) dans chaque marché",
                "impact": "FAIBLE - Ce champ est optionnel et peut être ignoré"
            })
        if "P" in first_market:
            differences.append({
                "type": "CHAMP SUPPLÉMENTAIRE DANS MARCHÉ",
                "field": "E[].P",
                "description": "La plateforme inclut le paramètre (P) pour certains marchés (over/under, handicap)",
                "impact": "MOYEN - Ce champ est important pour les marchés avec paramètres"
            })
    
    # 3. Structure AE différente
    if "AE" in platform_payload and platform_payload["AE"]:
        ae_structure = platform_payload["AE"][0]
        if "G" in ae_structure and "ME" in ae_structure:
            differences.append({
                "type": "STRUCTURE DIFFÉRENTE",
                "field": "AE",
                "description": "La plateforme utilise une structure imbriquée avec G et ME pour les marchés avancés",
                "impact": "ÉLEVÉ - Notre API attend une liste plate de marchés dans AE"
            })
    
    # 4. Noms de ligues
    platform_league = platform_payload["L"]
    api_league = api_expected["L"]
    if platform_league != api_league:
        differences.append({
            "type": "NOM DE LIGUE",
            "field": "L",
            "description": f"La plateforme utilise '{platform_league}' vs notre API attend '{api_league}'",
            "impact": "ÉLEVÉ - Les noms de ligues doivent correspondre exactement pour charger les modèles"
        })
    
    # Afficher les différences
    for i, diff in enumerate(differences, 1):
        print(f"\n{i}. {diff['type']} - {diff['field']}")
        print(f"   Description: {diff['description']}")
        print(f"   Impact: {diff['impact']}")
    
    print("\n" + "=" * 80)
    print("RECOMMANDATIONS")
    print("=" * 80)
    
    print("\n1. Mettre à jour l'API pour:")
    print("   - Accepter les champs optionnels: SC, B, G, P")
    print("   - Parser la structure imbriquée AE (G + ME)")
    print("   - Normaliser les noms de ligues")
    
    print("\n2. Créer un mapping de noms de ligues:")
    print("   - 'Ligue 1' -> 'FC 25. Championnat d'Angleterre' (ou autre ligue FIFA)")
    print("   - Mapper les noms de ligues de la plateforme vers nos noms FIFA")
    
    print("\n3. Tester avec les données réelles de la plateforme")
    print("   - Créer des fichiers de test avec le format exact")
    print("   - Valider que l'API peut traiter ces données")
    
    print("\n" + "=" * 80)
    
    return differences

def create_platform_test_data():
    """Crée des données de test au format de la plateforme"""
    
    test_data = {
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
    
    with open("platform_test_data.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Fichier de test créé: platform_test_data.json")
    print("   Ce fichier peut être utilisé pour tester l'API avec le format de la plateforme")

if __name__ == "__main__":
    analyze_platform_format()
    create_platform_test_data()
