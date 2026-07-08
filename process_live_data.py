"""
Traitement des Données Live de la Plateforme
============================================
Script pour traiter les données JSON de la plateforme de paris,
extraire les matchs, obtenir les prédictions via l'API, et combiner avec les cotes.

Author: SOLITAIRE HACK
Version: 1.0
"""

import requests
import json
from datetime import datetime

print("=== TRAITEMENT DES DONNÉES LIVE ===\n")

# Configuration
API_BASE_URL = "http://localhost:5000"

def parse_live_data(live_data):
    """Parse les données live de la plateforme"""
    if not live_data or 'Value' not in live_data:
        return []
    
    matches = []
    for match_data in live_data['Value']:
        match = {
            'match_id': match_data.get('I'),
            'team_home': match_data.get('O1'),
            'team_away': match_data.get('O2'),
            'league': match_data.get('L'),
            'timestamp': match_data.get('S'),
            'odds': match_data.get('E', []),
            'additional_odds': match_data.get('AE', []),
            'status': match_data.get('SC', {}).get('FS', {}),
            'time_remaining': match_data.get('SC', {}).get('TS', 0)
        }
        matches.append(match)
    
    return matches

def extract_odds(odds_list, odd_type, param=None):
    """Extrait une cote spécifique de la liste"""
    for odd in odds_list:
        if odd.get('T') == odd_type:
            if param is None or odd.get('P') == param:
                return {
                    'value': odd.get('C'),
                    'param': odd.get('P'),
                    'is_blocked': odd.get('B', False)
                }
    return None

def get_prediction_from_api(match):
    """Obtient la prédiction depuis notre API"""
    try:
        payload = {
            "I": match['match_id'],
            "O1": match['team_home'],
            "O2": match['team_away'],
            "L": match['league'],
            "S": match['timestamp']
        }
        
        response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'API error: {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def process_match(match):
    """Traite un match individuel"""
    print(f"\n--- Match: {match['team_home']} vs {match['team_away']} ---")
    print(f"Ligue: {match['league']}")
    print(f"ID: {match['match_id']}")
    
    # Obtenir la prédiction
    prediction = get_prediction_from_api(match)
    
    if not prediction.get('success'):
        print(f"Erreur prédiction: {prediction.get('error')}")
        return None
    
    # Extraire les cotes principales
    odds = match['odds']
    main_odds = {
        'home_win': extract_odds(odds, 1),
        'draw': extract_odds(odds, 2),
        'away_win': extract_odds(odds, 3),
        'btts_yes': extract_odds(odds, 5),
        'btts_no': extract_odds(odds, 6)
    }
    
    # Extraire les cotes Over/Under
    over_under_odds = []
    for odd in odds:
        if odd.get('T') in [9, 10]:  # Over/Under
            over_under_odds.append({
                'type': 'over' if odd.get('T') == 9 else 'under',
                'threshold': odd.get('P'),
                'value': odd.get('C')
            })
    
    # Combiner les données
    result = {
        'match': {
            'id': match['match_id'],
            'home': match['team_home'],
            'away': match['team_away'],
            'league': match['league'],
            'timestamp': match['timestamp'],
            'status': match['status'],
            'time_remaining': match['time_remaining']
        },
        'prediction': prediction,
        'platform_odds': {
            'main': main_odds,
            'over_under': over_under_odds
        }
    }
    
    # Afficher le résumé
    print(f"Prédiction résultat: {prediction['predictions']['match_result']['prediction']} (conf: {prediction['predictions']['match_result']['confidence']:.2f})")
    print(f"Prédiction buts: {prediction['predictions']['total_goals']['predicted']:.1f}")
    print(f"Cote Home Win: {main_odds['home_win']['value'] if main_odds['home_win'] else 'N/A'}")
    print(f"Cote Draw: {main_odds['draw']['value'] if main_odds['draw'] else 'N/A'}")
    print(f"Cote Away Win: {main_odds['away_win']['value'] if main_odds['away_win'] else 'N/A'}")
    
    return result

def process_live_data_json(live_data_json):
    """Traite le JSON complet des données live"""
    print(f"Réception des données live...")
    
    # Parser les données
    live_data = json.loads(live_data_json) if isinstance(live_data_json, str) else live_data_json
    matches = parse_live_data(live_data)
    
    print(f"Nombre de matchs trouvés: {len(matches)}")
    
    # Traiter chaque match
    results = []
    for match in matches:
        result = process_match(match)
        if result:
            results.append(result)
    
    # Générer le rapport final
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_matches': len(matches),
        'processed_matches': len(results),
        'matches': results
    }
    
    return report

# ─────────────────────────────────────────
# TEST AVEC LES DONNÉES FOURNIES
# ─────────────────────────────────────────

# Exemple de données live (à remplacer par les données réelles)
sample_live_data = {
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
                {"T": 8, "P": 1.5, "C": 1.485, "CV": "1.485", "G": 2},
                {"T": 9, "P": 7.5, "C": 1.504, "CV": "1.504", "G": 17},
                {"T": 12, "P": 4.5, "C": 1.775, "CV": "1.775", "G": 15},
                {"T": 11, "P": 4.5, "C": 2.045, "CV": "2.045", "G": 15},
                {"T": 10, "P": 7.5, "C": 2.5, "CV": "2.5", "G": 17},
                {"T": 7, "P": -1.5, "C": 2.565, "CV": "2.565", "G": 2},
                {"T": 13, "P": 3.5, "C": 3.3, "CV": "3.3", "G": 62},
                {"T": 6, "C": 5.23, "CV": "5.23", "G": 8},
                {"T": 2, "C": 6.14, "CV": "6.14", "G": 1},
                {"T": 3, "C": 30, "CV": "30", "G": 1}
            ],
            "AE": [
                {
                    "G": 2,
                    "ME": [
                        {"T": 7, "P": -1.0, "C": 1.384, "CV": "1.384", "G": 2},
                        {"T": 8, "P": 1.0, "C": 2.93, "CV": "2.93", "G": 2},
                        {"T": 7, "P": -1.5, "C": 2.565, "CV": "2.565", "G": 2, "CE": 1},
                        {"T": 8, "P": 1.5, "C": 1.485, "CV": "1.485", "G": 2, "CE": 1}
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

if __name__ == "__main__":
    # Traiter les données live
    report = process_live_data_json(sample_live_data)
    
    # Sauvegarder le rapport
    with open('live_predictions_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== RAPPORT SAUVEGARDÉ ===")
    print(f"Fichier: live_predictions_report.json")
    print(f"Matchs traités: {report['processed_matches']}/{report['total_matches']}")
