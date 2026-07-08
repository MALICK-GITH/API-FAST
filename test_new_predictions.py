import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import json
from league_family_mapping import get_league_family, get_family_options, map_prediction_to_platform

print("=== TEST DES NOUVEAUX MODÈLES (Over/Under et BTTS) ===\n")

# Charger les modèles
print("Chargement des modèles...")
model = joblib.load('fifa_prediction_model.pkl')
feature_columns = joblib.load('feature_columns.pkl')
overunder_model = joblib.load('overunder_model.pkl')
overunder_feature_columns = joblib.load('overunder_feature_columns.pkl')
btts_model = joblib.load('btts_model.pkl')
btts_feature_columns = joblib.load('btts_feature_columns.pkl')
team_stats = pd.read_csv('team_stats.csv')
league_stats = pd.read_csv('training_features.csv')[['league', 'avg_total_goals']].drop_duplicates()

print("Modèles chargés avec succès!\n")

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
                "S": 1783473000,
                "O1": "Club Atlético de Madrid",
                "O2": "Porto",
                "L": "FC 26. 5x5 Rush. Superligue"
            },
            "ST": "Paris avant le début du jeu",
            "I": 734797802,
            "S": 1783473000,
            "O1": "Club Atlético de Madrid",
            "O2": "Porto",
            "L": "FC 26. 5x5 Rush. Superligue"
        },
        {
            "R": 50,
            "SC": {
                "FS": {},
                "PS": [],
                "CPS": "",
                "GS": 128,
                "TS": 234,
                "TD": -1,
                "I": "",
                "S": 1783472400,
                "O1": "Galatasaray",
                "O2": "Bayer 04",
                "L": "FC 26. 5x5 Rush. Superligue"
            },
            "ST": "",
            "I": 734796647,
            "S": 1783472400,
            "O1": "Galatasaray",
            "O2": "Bayer 04",
            "L": "FC 26. 5x5 Rush. Superligue"
        },
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
                "S": 1783473600,
                "O1": "Juventus",
                "O2": "Real Madrid",
                "L": "FC 26. 5x5 Rush. Superligue"
            },
            "ST": "Paris avant le début du jeu",
            "I": 734799022,
            "S": 1783473600,
            "O1": "Juventus",
            "O2": "Real Madrid",
            "L": "FC 26. 5x5 Rush. Superligue"
        }
    ]
}

matches = json_data['Value']
print(f"{len(matches)} matchs à prédire\n")

print("=== PRÉDICTIONS SUR LES MATCHS RÉELS ===\n")

predictions = []
success_count = 0
error_count = 0

for i, match in enumerate(matches, 1):
    try:
        features = prepare_features(match)
        
        # Obtenir la famille de la ligue
        league = match['L']
        family = get_league_family(league)
        family_options = get_family_options(family)
        
        # Prédiction du résultat
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        result_map = {0: 'away_win', 1: 'draw', 2: 'home_win'}
        result_text = result_map[prediction]
        
        # Prédiction Over/Under (seuil ajusté selon la famille)
        overunder_threshold = family_options['over_under_threshold']
        overunder_features = features[overunder_feature_columns]
        overunder_pred = overunder_model.predict(overunder_features)[0]
        overunder_proba = overunder_model.predict_proba(overunder_features)[0]
        overunder_text = 'over' if overunder_pred == 1 else 'under'
        
        # Prédiction BTTS
        btts_features = features[btts_feature_columns]
        btts_pred = btts_model.predict(btts_features)[0]
        btts_proba = btts_model.predict_proba(btts_features)[0]
        btts_text = 'yes' if btts_pred == 1 else 'no'
        
        # Mapper les prédictions aux options de la plateforme
        total_goals_pred = features['avg_total_goals'].iloc[0]
        handicap_pred = features['goal_diff_avg'].iloc[0]
        
        total_goals_platform, total_goals_name = map_prediction_to_platform('total_goals', total_goals_pred, family)
        handicap_platform, handicap_name = map_prediction_to_platform('handicap', handicap_pred, family)
        
        print(f"Match {i}: {match['O1']} vs {match['O2']}")
        print(f"Ligue: {league}")
        print(f"Famille: {family}")
        print(f"Status: {match.get('ST', '')}")
        print(f"Résultat: {result_text} (confiance: {max(probabilities)*100:.2f}%)")
        print(f"Over/Under ({overunder_threshold}): {overunder_text} (confiance: {max(overunder_proba)*100:.2f}%)")
        print(f"BTTS: {btts_text} (confiance: {max(btts_proba)*100:.2f}%)")
        print(f"Total Goals: {total_goals_pred:.1f} -> Plateforme: {total_goals_platform} ({total_goals_name})")
        print(f"Handicap: {handicap_pred:+.1f} -> Plateforme: {handicap_platform:+.1f} ({handicap_name})")
        print()
        
        prediction_data = {
            'match_id': match.get('I', 'unknown'),
            'team_home': match['O1'],
            'team_away': match['O2'],
            'league': league,
            'family': family,
            'match_result': {
                'prediction': result_text,
                'confidence': float(max(probabilities)),
                'probabilities': {
                    'away_win': float(probabilities[0]),
                    'draw': float(probabilities[1]),
                    'home_win': float(probabilities[2])
                }
            },
            'over_under': {
                'threshold': overunder_threshold,
                'prediction': overunder_text,
                'confidence': float(max(overunder_proba)),
                'probabilities': {
                    'under': float(overunder_proba[0]),
                    'over': float(overunder_proba[1])
                }
            },
            'btts': {
                'prediction': btts_text,
                'confidence': float(max(btts_proba)),
                'probabilities': {
                    'no': float(btts_proba[0]),
                    'yes': float(btts_proba[1])
                }
            },
            'platform_mapping': {
                'total_goals': {
                    'predicted': float(total_goals_pred),
                    'platform_value': total_goals_platform,
                    'platform_name': total_goals_name
                },
                'handicap': {
                    'predicted': float(handicap_pred),
                    'platform_value': handicap_platform,
                    'platform_name': handicap_name
                }
            },
            'timestamp': match.get('S', datetime.now().timestamp())
        }
        
        predictions.append(prediction_data)
        success_count += 1
        
    except Exception as e:
        print(f"Erreur pour le match {i}: {str(e)}")
        error_count += 1

print("=== RÉSULTAT AU FORMAT JSON ===")
result_json = {
    'success': True,
    'predictions': predictions
}
print(json.dumps(result_json, indent=2, ensure_ascii=False))
print()

print("=== STATISTIQUES ===")
print(f"Nombre de matchs traités: {len(matches)}")
print(f"Prédictions réussies: {success_count}")
print(f"Erreurs: {error_count}")

if success_count > 0:
    avg_confidence_result = np.mean([p['match_result']['confidence'] for p in predictions])
    avg_confidence_overunder = np.mean([p['over_under']['confidence'] for p in predictions])
    avg_confidence_btts = np.mean([p['btts']['confidence'] for p in predictions])
    
    print(f"Confiance moyenne (Résultat): {avg_confidence_result*100:.2f}%")
    print(f"Confiance moyenne (Over/Under): {avg_confidence_overunder*100:.2f}%")
    print(f"Confiance moyenne (BTTS): {avg_confidence_btts*100:.2f}%")
    
    # Distribution des prédictions
    result_dist = {}
    overunder_dist = {}
    btts_dist = {}
    
    for p in predictions:
        result_dist[p['match_result']['prediction']] = result_dist.get(p['match_result']['prediction'], 0) + 1
        overunder_dist[p['over_under']['prediction']] = overunder_dist.get(p['over_under']['prediction'], 0) + 1
        btts_dist[p['btts']['prediction']] = btts_dist.get(p['btts']['prediction'], 0) + 1
    
    print("\nDistribution des prédictions:")
    print(f"Résultat: {result_dist}")
    print(f"Over/Under: {overunder_dist}")
    print(f"BTTS: {btts_dist}")

print("\n=== TEST TERMINÉ ===")
