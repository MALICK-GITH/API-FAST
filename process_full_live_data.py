"""
Traitement Complet des Données Live de la Plateforme
=====================================================
Script pour traiter le JSON complet avec tous les matchs live,
obtenir les prédictions via l'API, et combiner avec les cotes.

Author: SOLITAIRE HACK
Version: 1.0
"""

import requests
import json
from datetime import datetime
import time

print("=== TRAITEMENT COMPLET DES DONNÉES LIVE ===\n")

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
                return {'value': odd.get('C'), 'param': odd.get('P')}
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
        return {'error': f'API error: {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def process_match(match, index, total):
    """Traite un match individuel"""
    print(f"[{index}/{total}] {match['team_home']} vs {match['team_away']} ({match['league']})")
    
    prediction = get_prediction_from_api(match)
    
    if not prediction.get('success'):
        print(f"  ✗ Erreur: {prediction.get('error')}")
        return None
    
    odds = match['odds']
    main_odds = {
        'home_win': extract_odds(odds, 1),
        'draw': extract_odds(odds, 2),
        'away_win': extract_odds(odds, 3)
    }
    
    result = {
        'match': {'id': match['match_id'], 'home': match['team_home'], 'away': match['team_away'], 'league': match['league']},
        'prediction': prediction,
        'platform_odds': main_odds
    }
    
    pred = prediction['predictions']['match_result']
    print(f"  ✓ {pred['prediction']} (conf: {pred['confidence']:.2f})")
    
    return result

def process_live_data_json(live_data_json):
    """Traite le JSON complet des données live"""
    live_data = json.loads(live_data_json) if isinstance(live_data_json, str) else live_data_json
    matches = parse_live_data(live_data)
    
    print(f"Matchs trouvés: {len(matches)}")
    
    results = []
    for i, match in enumerate(matches, 1):
        result = process_match(match, i, len(matches))
        if result:
            results.append(result)
        if i < len(matches):
            time.sleep(0.5)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_matches': len(matches),
        'processed_matches': len(results),
        'matches': results
    }

if __name__ == "__main__":
    # Lire depuis un fichier JSON externe
    try:
        with open('live_data_input.json', 'r', encoding='utf-8') as f:
            live_data = json.load(f)
        
        report = process_live_data_json(live_data)
        
        with open('live_predictions_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== RAPPORT SAUVEGARDÉ ===")
        print(f"Matchs traités: {report['processed_matches']}/{report['total_matches']}")
    except FileNotFoundError:
        print("Erreur: Fichier 'live_data_input.json' non trouvé.")
        print("Sauvegardez les données JSON de la plateforme dans ce fichier.")
