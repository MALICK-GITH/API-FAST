"""
Analyse du Format de la Plateforme de Paris
===========================================
Analyse détaillée du format JSON de la plateforme pour adapter l'API

Author: SOLITAIRE HACK
Version: 1.0
"""

import json

print("=== ANALYSE DU FORMAT DE LA PLATEFORME ===\n")

# Données JSON fournies par l'utilisateur
PLATFORM_JSON = {
    "Id": 0,
    "Success": True,
    "Error": "",
    "ErrorCode": 0,
    "Guid": "",
    "Value": [
        {
            "R": 50,
            "SC": {"FS": {"S1": 4, "S2": 3}, "PS": [], "CPS": "", "TS": 368, "I": "", "SLS": "6 minutes"},
            "VI": "xgame7_53465269",
            "VA": 1,
            "HMH": 1,
            "ICY": True,
            "U": 1783516786,
            "I": 734915710,
            "N": 251259,
            "T": 50,
            "CO": 17,
            "E": [
                {"T": 4, "C": 1.001, "CV": "1.001", "B": True, "G": 8},
                {"T": 5, "C": 1.06, "CV": "1.06", "G": 8},
                {"T": 1, "C": 1.096, "CV": "1.096", "G": 1},
                {"T": 14, "P": 3.5, "C": 1.312, "CV": "1.312", "G": 62},
                {"T": 8, "P": 1.5, "C": 1.485, "CV": 1.485", "G": 2},
                {"T": 9, "P": 7.5, "C": 1.504, "CV": 1.504", "G": 17},
                {"T": 12, "P": 4.5, "C": 1.775, "CV": "1.775", "G": 15},
                {"T": 11, "P": 4.5, "C": 2.045, "CV": "2.045", "G": 15},
                {"T": 10, "P": 7.5, "C": 2.5, "CV": 2.5", "G": 17},
                {"T": 7, "P": -1.5, "C": 2.565, "CV": "2.565", "G": 2},
                {"T": 13, "P": 3.5, "C": 3.3, "CV": "3.3", "G": 62},
                {"T": 6, "C": 5.23, "CV": 5.23", "G": 8},
                {"T": 2, "C": 6.14, "CV": 6.14", "G": 1},
                {"T": 3, "C": 30, "CV": 30, "G": 1}
            ],
            "AE": [
                {
                    "G": 2,
                    "ME": [
                        {"T": 7, "P": -1.0, "C": 1.384, "CV": "1.384", "G": 2},
                        {"T": 8, "P": 1.0, "C": 2.93, "CV": "2.93", "G": 2},
                        {"T": 7, "P": -1.5, "C": 2.565, "CV": 2.565", "G": 2, "CE": 1},
                        {"T": 8, "P": 1.5, "C": 1.485, "CV": 1.485, "G": 2, "CE": 1}
                    ]
                },
                {
                    "G": 17,
                    "ME": [
                        {"T": 9, "P": 7.5, "C": 1.504, "CV": 1.504", "G": 17, "CE": 1},
                        {"T": 10, "P": 7.5, "C": 2.5, "CV": 2.5", "G": 17, "CE": 1},
                        {"T": 9, "P": 8.5, "C": 3.84, "CV": 3.84", "G": 17},
                        {"T": 10, "P": 8.5, "C": 1.22, "CV": 1.22", "G": 17}
                    ]
                }
            ],
            "EC": 39,
            "TG": "",
            "V": "",
            "VE": "",
            "PN": "",
            "TN": "Mi-temps",
            "DI": "",
            "S": 1783516200,
            "HS": 1,
            "SGC": 1,
            "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
            "O1": "Barcelone",
            "O2": "Galatasaray",
            "O1I": 180071,
            "O2I": 202115,
            "O1IS": [180071],
            "O2IS": [202115],
            "O1C": 78,
            "O1CT": "Barcelona",
            "O2C": 190,
            "O2CT": "Istanbul",
            "O1IMG": ["180071.png"],
            "O2IMG": ["202115.png"],
            "O1R": "Барселона",
            "O2R": "Галатасарай",
            "O1E": "Barcelona",
            "O2E": "Galatasaray",
            "SI": 85,
            "SN": "FIFA",
            "SR": "FIFA",
            "SE": "FIFA",
            "L": "FC 26. 5x5 Rush. Superligue",
            "LR": "FC 26. 5x5 Rush. Суперлига",
            "LE": "FC 26. 5x5 Rush. Superleague",
            "LI": 2986291,
            "CN": "Monde",
            "CE": "World",
            "COI": 225,
            "MS": [0],
            "KI": 1,
            "CID": 2,
            "SIMG": "/genfiles/cms/sport_preview_5a598a83300665a1d4192948ea1362e5.png",
            "TNS": "Mi-temps"
        }
    ]
}

print("=== STRUCTURE DU JSON ===\n")

print("Racine: Id, Success, Error, ErrorCode, Guid")
print("Donnees: Value[] - tableau de matchs\n")

print("=== CHAMPS D'UN MATCH ===\n")

match = PLATFORM_JSON['Value'][0]

print("Identifiants:")
print(f"  I (Match ID): {match['I']}")
print(f"  N (Nombre): {match['N']}")
print(f"  T (Type): {match['T']}")
print(f"  CO (Country ID): {match['CO']}")

print("\nÉquipes:")
print(f"  O1 (Home): {match['O1']}")
print(f"  O2 (Away): {match['O2']}")
print(f"  O1I (Home ID): {match['O1I']}")
print(f"  O2I (Away ID): {match['O2I']}")
print(f"  O1E (Home EN): {match['O1E']}")
print(f"  O2E (Away EN): {match['O2E']}")

print("\nLigue:")
print(f"  L (Nom): {match['L']}")
print(f"  LI (League ID): {match['LI']}")
print(f"  CE (Country): {match['CE']}")
print(f"  CN (Continent): {match['CN']}")

print("\nScore et Temps:")
print(f"  SC.FS (Score Final): {match['SC']['FS']}")
print(f"  SC.TS (Temps restant): {match['SC']['TS']}")
print(f"  SC.I (Info): {match['SC']['I']}")
print(f"  S (Timestamp): {match['S']}")
print(f"  SLS (Status long): {match['SC']['SLS']}")

print("\nCotes Principales (E):")
for odd in match['E'][:5]:
    print(f"  Type {odd['T']}: Cote={odd['C']}, Param={odd.get('P', 'N/A')}, Blocked={odd.get('B', False)}")

print("\nCotes Additionnelles (AE):")
for group in match['AE']:
    print(f"  Groupe {group['G']}:")
    for odd in group['ME'][:3]:
        print(f"    Type {odd['T']}: Cote={odd['C']}, Param={odd.get('P', 'N/A')}, Current={odd.get('CE', False)}")

print("\n=== MAPPING POUR L'API ===\n")

print("Champs API -> Champs Plateforme:")
print("  match_id -> I")
print("  team_home -> O1")
print("  team_away -> O2")
print("  league -> L")
print("  timestamp -> S")
print("  odds -> E[]")

print("\n=== FORMAT D'ENTRÉE API ===\n")

api_input_format = {
    "match_id": "I",
    "team_home": "O1",
    "team_away": "O2",
    "league": "L",
    "timestamp": "S",
    "odds": "E[]"
}

print("Format attendu par notre API:")
for api_field, platform_field in api_input_format.items():
    print(f"  {api_field}: {platform_field}")

print("\n=== FORMAT DE SORTIE API ===\n")

api_output_format = {
    "success": True,
    "match_id": "I",
    "team_home": "O1",
    "team_away": "O2",
    "league": "L",
    "predictions": {
        "match_result": {"prediction": "home_win|draw|away_win", "confidence": 0.0-1.0},
        "total_goals": {"predicted": float, "platform_value": float},
        "total_parity": {"prediction": "even|odd", "confidence": 0.0-1.0},
        "over_under": {"threshold": float, "prediction": "over|under"}
    },
    "platform_mapping": {
        "total_goals": {"predicted": float, "platform_value": float},
        "handicap": {"predicted": float, "platform_value": float}
    },
    "platform_odds": {
        "main": {
            "home_win": {"value": float},
            "draw": {"value": float},
            "away_win": {"value": float}
        },
        "over_under": [
            {"type": "over|under", "threshold": float, "value": float}
        ],
        "handicap": [
            {"type": "home|away", "handicap": float, "value": float}
        ]
    }
}

print("Format de réponse de notre API:")
print(json.dumps(api_output_format, indent=2, ensure_ascii=False))

print("\n=== CODES DE COTE (E.T) ===\n")
print("Codes principaux:")
print("  T=1: Home Win")
print("  T=2: Draw")
print("  T=3: Away Win")
print("  T=4: No Bet")
print("  T=5: BTTS No")
print("  T=6: BTTS Yes")
print("  T=7: Home Handicap")
print("  T=8: Away Handicap")
print("  T=9: Over")
print("  T=10: Under")
print("  T=11: Over/Under (variant)")
print("  T=12: Over/Under (variant)")
print("  T=13: Over/Under (variant)")
print("  T=14: Over/Under (variant)")
print("  T=180: Double Chance")
print("  T=181: Double Chance (variant)")

print("\n=== CODES DE GROUPE (AE.G) ===\n")
print("Codes de groupe:")
print("  G=2: Handicap")
print("  G=17: Total Goals")

print("\n=== CONCLUSION ===\n")
print("L'API doit:")
print("1. Accepter le format JSON exact de la plateforme")
print("2. Parser les champs O1, O2, L, S, E pour les prédictions")
print("3. Retourner le format JSON attendu par les plateformes")
print("4. Inclure les cotes de la plateforme dans la réponse")
