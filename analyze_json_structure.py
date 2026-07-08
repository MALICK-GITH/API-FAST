import json
import pandas as pd

# Exemple de JSON reçu du système
json_data = """
{
    "Id": 0,
    "Success": true,
    "Error": "",
    "ErrorCode": 0,
    "Guid": "",
    "Value": [
        {
            "R": 50,
            "SC": {
                "FS": {},
                "PS": [],
                "CPS": "",
                "GS": 128,
                "TS": 1009,
                "TD": -1,
                "I": "Paris avant le début du jeu",
                "SLS": "Début dans 17 minutes"
            },
            "GNS": true,
            "ICY": true,
            "U": 1783471991,
            "I": 734797802,
            "N": 232519,
            "T": 50,
            "CO": 17,
            "E": [
                {"T": 5, "C": 1.07, "CV": "1.07", "G": 8},
                {"T": 4, "C": 1.33, "CV": "1.33", "G": 8},
                {"T": 1, "C": 1.725, "CV": "1.725", "G": 1},
                {"T": 3, "C": 2.992, "CV": "2.992", "G": 1},
                {"T": 2, "C": 5.91, "CV": "5.91", "G": 1}
            ],
            "O1": "Club Atlético de Madrid",
            "O2": "Porto",
            "O1I": 180445,
            "O2I": 202125,
            "L": "FC 26. 5x5 Rush. Superligue",
            "S": 1783473000,
            "TN": "Mi-temps"
        }
    ]
}
"""

# Charger et analyser le JSON
data = json.loads(json_data)
matches = data['Value']

print("=== STRUCTURE JSON DES MATCHS À PRÉDIRE ===\n")

# Analyser la structure d'un match
for match in matches[:3]:  # Analyser les 3 premiers matchs
    print(f"Match ID: {match['I']}")
    print(f"Équipe domicile (O1): {match['O1']} (ID: {match['O1I']})")
    print(f"Équipe extérieur (O2): {match['O2']} (ID: {match['O2I']})")
    print(f"Ligue: {match['L']}")
    print(f"Timestamp: {match['S']}")
    print(f"Status: {match['SC']['I'] if 'I' in match['SC'] else 'N/A'}")
    
    print("\nCotes disponibles (E):")
    for odd in match['E']:
        odd_type = odd['T']
        odd_value = odd['C']
        odd_group = odd['G']
        
        # Types de cotes courants
        type_names = {
            1: "Victoire domicile",
            2: "Victoire extérieur", 
            3: "Match nul",
            4: "Double chance (1X)",
            5: "Double chance (12)",
            6: "Double chance (X2)",
            7: "Handicap domicile",
            8: "Handicap extérieur",
            9: "Over buts",
            10: "Under buts",
            11: "Over buts domicile",
            12: "Under buts domicile",
            13: "Over buts extérieur",
            14: "Under buts extérieur"
        }
        
        type_name = type_names.get(odd_type, f"Type {odd_type}")
        print(f"  - {type_name}: {odd_value} (Groupe: {odd_group})")
    
    print("\n" + "="*60 + "\n")

# Créer un DataFrame avec les données extraites
extracted_data = []
for match in matches:
    # Extraire les cotes principales
    odds_dict = {}
    for odd in match['E']:
        odds_dict[f"odd_type_{odd['T']}"] = odd['C']
    
    extracted_data.append({
        'match_id': match['I'],
        'team_home': match['O1'],
        'team_away': match['O2'],
        'team_home_id': match['O1I'],
        'team_away_id': match['O2I'],
        'league': match['L'],
        'timestamp': match['S'],
        'status': match['SC']['I'] if 'I' in match['SC'] else 'not_started',
        **odds_dict
    })

df_matches = pd.DataFrame(extracted_data)
print("=== DATAFRAME EXTRAIT ===")
print(df_matches.head())
print(f"\nColonnes disponibles: {df_matches.columns.tolist()}")
