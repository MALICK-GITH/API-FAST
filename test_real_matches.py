import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import json

print("=== TEST DU MODÈLE AVEC DONNÉES RÉELLES ===\n")

# Charger le modèle et les features
print("Chargement du modèle...")
model = joblib.load('fifa_prediction_model.pkl')
feature_columns = joblib.load('feature_columns.pkl')
team_stats = pd.read_csv('team_stats.csv')

# Charger les features d'entraînement pour obtenir les stats de ligue
df_features = pd.read_csv('training_features.csv')
league_stats = df_features[['league', 'avg_total_goals']].drop_duplicates()

print("Modèle chargé avec succès!\n")

def get_team_stats(team_name):
    """Récupère les statistiques d'une équipe"""
    stats = team_stats[team_stats['team'] == team_name]
    if len(stats) > 0:
        return stats.iloc[0].to_dict()
    else:
        return {
            'win_rate': 0.5,
            'draw_rate': 0.2,
            'avg_goals_scored': 2.0,
            'avg_goals_conceded': 2.0
        }

def get_league_stats(league_name):
    """Récupère les statistiques d'une ligue"""
    stats = league_stats[league_stats['league'] == league_name]
    if len(stats) > 0:
        return stats.iloc[0]['avg_total_goals']
    else:
        return 3.0

def prepare_features(match_data):
    """Prépare les features pour la prédiction"""
    team_home = match_data['O1']
    team_away = match_data['O2']
    league = match_data['L']
    
    home_stats = get_team_stats(team_home)
    away_stats = get_team_stats(team_away)
    avg_total_goals = get_league_stats(league)
    
    goal_diff_avg = home_stats['avg_goals_scored'] - away_stats['avg_goals_scored']
    win_rate_diff = home_stats['win_rate'] - away_stats['win_rate']
    
    top_leagues = league_stats['league'].value_counts().head(20).index.tolist()
    league_encoded = 1 if league in top_leagues else 0
    
    timestamp = match_data.get('S', datetime.now().timestamp())
    date = datetime.fromtimestamp(timestamp)
    
    features = {
        'home_team_win_rate': home_stats['win_rate'],
        'home_team_draw_rate': home_stats['draw_rate'],
        'home_team_avg_goals_scored': home_stats['avg_goals_scored'],
        'home_team_avg_goals_conceded': home_stats['avg_goals_conceded'],
        'away_team_win_rate': away_stats['win_rate'],
        'away_team_draw_rate': away_stats['draw_rate'],
        'away_team_avg_goals_scored': away_stats['avg_goals_scored'],
        'away_team_avg_goals_conceded': away_stats['avg_goals_conceded'],
        'avg_total_goals': avg_total_goals,
        'goal_diff_avg': goal_diff_avg,
        'win_rate_diff': win_rate_diff,
        'league_encoded': league_encoded,
        'year': date.year,
        'month': date.month,
        'day_of_week': date.weekday()
    }
    
    return pd.DataFrame([features])

def predict_match(match_data):
    """Prédit le résultat d'un match"""
    try:
        features = prepare_features(match_data)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        result_map = {0: 'away_win', 1: 'draw', 2: 'home_win'}
        result_text = result_map[prediction]
        
        return {
            'match_id': match_data.get('I', 'unknown'),
            'team_home': match_data['O1'],
            'team_away': match_data['O2'],
            'league': match_data['L'],
            'prediction': result_text,
            'confidence': float(max(probabilities)),
            'probabilities': {
                'away_win': float(probabilities[0]),
                'draw': float(probabilities[1]),
                'home_win': float(probabilities[2])
            },
            'timestamp': match_data.get('S', datetime.now().timestamp())
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'match_id': match_data.get('I', 'unknown')
        }

# JSON réel fourni par l'utilisateur
json_data = {
    "Id": 0,
    "Success": True,
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
                "TS": 234,
                "TD": -1,
                "I": "Paris avant le début du jeu",
                "SLS": "Début dans 4 minutes"
            },
            "HMH": 1,
            "GNS": True,
            "ICY": True,
            "U": 1783472766,
            "I": 734797802,
            "N": 232519,
            "T": 50,
            "CO": 17,
            "E": [
                {"T": 5, "C": 1.07, "CV": "1.07", "G": 8},
                {"T": 4, "C": 1.33, "CV": "1.33", "G": 8},
                {"T": 1, "C": 1.725, "CV": "1.725", "G": 1},
                {"T": 8, "P": 1.0, "C": 1.736, "CV": "1.736", "G": 2},
                {"T": 13, "P": 2.5, "C": 1.736, "CV": "1.736", "G": 62},
                {"T": 10, "P": 6.5, "C": 1.81, "CV": "1.81", "G": 17},
                {"T": 12, "P": 3.5, "C": 1.875, "CV": "1.875", "G": 15},
                {"T": 11, "P": 3.5, "C": 1.925, "CV": "1.925", "G": 15},
                {"T": 9, "P": 6.5, "C": 2, "CV": "2", "G": 17},
                {"T": 6, "C": 2.02, "CV": "2.02", "G": 8},
                {"T": 7, "P": -1.0, "C": 2.096, "CV": "2.096", "G": 2},
                {"T": 14, "P": 2.5, "C": 2.1, "CV": "2.1", "G": 62},
                {"T": 3, "C": 2.992, "CV": "2.992", "G": 1},
                {"T": 2, "C": 5.91, "CV": "5.91", "G": 1}
            ],
            "EC": 97,
            "TG": "",
            "V": "",
            "VE": "",
            "PN": "",
            "TN": "Mi-temps",
            "DI": "",
            "S": 1783473000,
            "HS": 1,
            "SGC": 1,
            "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
            "O1": "Club Atlético de Madrid",
            "O2": "Porto",
            "O1I": 180445,
            "O2I": 202125,
            "O1IS": [180445],
            "O2IS": [202125],
            "O1C": 78,
            "O1CT": "Madrid",
            "O2C": 148,
            "O2CT": "Porto",
            "O1IMG": ["180445.png"],
            "O2IMG": ["202125.png"],
            "O1R": "Атлетико Мадрид",
            "O2R": "Порту",
            "O1E": "Atletico Madrid",
            "O2E": "Porto",
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
        },
        {
            "R": 50,
            "SC": {
                "FS": {"S1": 3, "S2": 1},
                "PS": [],
                "CPS": "",
                "TS": 217,
                "I": "",
                "SLS": "3 minutes"
            },
            "VI": "xgame7_53452626",
            "VA": 1,
            "HMH": 1,
            "ICY": True,
            "U": 1783472766,
            "I": 734796647,
            "N": 223766,
            "T": 50,
            "CO": 17,
            "E": [
                {"T": 4, "C": 1.01, "CV": "1.01", "G": 8},
                {"T": 5, "C": 1.03, "CV": "1.03", "G": 8},
                {"T": 1, "C": 1.17, "CV": "1.17", "G": 1},
                {"T": 13, "P": 2.5, "C": 1.6, "CV": "1.6", "G": 62},
                {"T": 11, "P": 4.5, "C": 1.66, "CV": "1.66", "G": 15},
                {"T": 9, "P": 7.5, "C": 1.725, "CV": "1.725", "G": 17},
                {"T": 8, "P": 2.0, "C": 1.835, "CV": "1.835", "G": 2},
                {"T": 7, "P": -2.0, "C": 1.97, "CV": "1.97", "G": 2},
                {"T": 10, "P": 7.5, "C": 2.112, "CV": "2.112", "G": 17},
                {"T": 12, "P": 4.5, "C": 2.225, "CV": "2.225", "G": 15},
                {"T": 14, "P": 2.5, "C": 2.336, "CV": "2.336", "G": 62},
                {"T": 6, "C": 4, "CV": "4", "G": 8},
                {"T": 2, "C": 7.4, "CV": "7.4", "G": 1},
                {"T": 3, "C": 8.7, "CV": "8.7", "G": 1}
            ],
            "EC": 77,
            "TG": "",
            "V": "",
            "VE": "",
            "PN": "",
            "TN": "Mi-temps",
            "DI": "",
            "S": 1783472400,
            "HS": 1,
            "SGC": 1,
            "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
            "O1": "Galatasaray",
            "O2": "Bayer 04",
            "O1I": 202115,
            "O2I": 202197,
            "O1IS": [202115],
            "O2IS": [202197],
            "O1C": 190,
            "O1CT": "Istanbul",
            "O2C": 53,
            "O2CT": "Leverkusen",
            "O1IMG": ["202115.png"],
            "O2IMG": ["bd1179b754fc2fd2408a601199a5af46.png"],
            "O1R": "Галатасарай",
            "O2R": "Байер 04",
            "O1E": "Galatasaray",
            "O2E": "Bayer 04",
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
        },
        {
            "R": 50,
            "SC": {
                "FS": {},
                "PS": [],
                "CPS": "",
                "GS": 128,
                "TS": 834,
                "TD": -1,
                "TR": -1,
                "I": "Paris avant le début du jeu",
                "SLS": "Début dans 14 minutes"
            },
            "HMH": 1,
            "GNS": True,
            "ICY": True,
            "U": 1783472766,
            "I": 734799022,
            "N": 156273,
            "T": 50,
            "CO": 17,
            "E": [
                {"T": 5, "C": 1.032, "CV": "1.032", "G": 8},
                {"T": 6, "C": 1.155, "CV": "1.155", "G": 8},
                {"T": 3, "C": 1.395, "CV": "1.395", "G": 1},
                {"T": 11, "P": 2.5, "C": 1.616, "CV": "1.616", "G": 15},
                {"T": 8, "P": -1.5, "C": 1.84, "CV": "1.84", "G": 2},
                {"T": 9, "P": 7.5, "C": 1.86, "CV": "1.86", "G": 17},
                {"T": 13, "P": 4.5, "C": 1.885, "CV": "1.885", "G": 62},
                {"T": 14, "P": 4.5, "C": 1.915, "CV": "1.915", "G": 62},
                {"T": 10, "P": 7.5, "C": 1.94, "CV": "1.94", "G": 17},
                {"T": 7, "P": 1.5, "C": 1.965, "CV": "1.965", "G": 2},
                {"T": 12, "P": 2.5, "C": 2.304, "CV": "2.304", "G": 15},
                {"T": 4, "C": 2.696, "CV": "2.696", "G": 8},
                {"T": 1, "C": 4.16, "CV": "4.16", "G": 1},
                {"T": 2, "C": 7.31, "CV": "7.31", "G": 1}
            ],
            "EC": 102,
            "TG": "",
            "V": "",
            "VE": "",
            "PN": "",
            "TN": "Mi-temps",
            "DI": "",
            "S": 1783473600,
            "HS": 1,
            "SGC": 1,
            "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
            "O1": "Juventus",
            "O2": "Real Madrid",
            "O1I": 180451,
            "O2I": 180075,
            "O1IS": [180451],
            "O2IS": [180075],
            "O1C": 79,
            "O2C": 78,
            "O2CT": "Madrid",
            "O1IMG": ["180451.png"],
            "O2IMG": ["180075.png"],
            "O1R": "Ювентус",
            "O2R": "Реал",
            "O1E": "Juventus",
            "O2E": "Real Madrid",
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

# Tester les prédictions sur les matchs réels
print("=== PRÉDICTIONS SUR LES MATCHS RÉELS ===\n")

matches = json_data['Value']
predictions = []

for i, match in enumerate(matches, 1):
    print(f"Match {i}: {match['O1']} vs {match['O2']}")
    print(f"Ligue: {match['L']}")
    print(f"Status: {match['SC'].get('I', 'N/A')}")
    
    try:
        prediction = predict_match(match)
        predictions.append(prediction)
        
        print(f"Prédiction: {prediction['prediction']}")
        print(f"Confiance: {prediction['confidence']:.2%}")
        print(f"Probabilités:")
        print(f"  - Victoire domicile: {prediction['probabilities']['home_win']:.2%}")
        print(f"  - Match nul: {prediction['probabilities']['draw']:.2%}")
        print(f"  - Victoire extérieur: {prediction['probabilities']['away_win']:.2%}")
    except Exception as e:
        print(f"Erreur: {e}")
        predictions.append({'error': str(e), 'match_id': match.get('I', 'unknown')})
    
    print()

# Résultat au format JSON
result = {
    'success': True,
    'predictions': predictions
}

print("=== RÉSULTAT AU FORMAT JSON ===")
print(json.dumps(result, indent=2, ensure_ascii=False))

# Statistiques
print("\n=== STATISTIQUES ===")
print(f"Nombre de matchs traités: {len(predictions)}")
print(f"Prédictions réussies: {sum(1 for p in predictions if 'error' not in p)}")
print(f"Erreurs: {sum(1 for p in predictions if 'error' in p)}")

if len(predictions) > 0:
    avg_confidence = np.mean([p['confidence'] for p in predictions if 'confidence' in p])
    print(f"Confiance moyenne: {avg_confidence:.2%}")

print("\n=== TEST TERMINÉ ===")
