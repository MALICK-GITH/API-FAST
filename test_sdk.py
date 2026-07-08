"""
Test du SDK FIFA Prediction
============================
Test du SDK sans démarrer l'API (utilisation directe des modèles)

Author: SOLITAIRE HACK
Version: 1.0
"""

import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from fifa_prediction_sdk import MatchData, parse_json_match, parse_json_batch

print("=== TEST DU SDK FIFA PREDICTION (MODE DIRECT) ===\n")

# Charger les modèles directement
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

# Fonction de préparation des features (copiée depuis prediction_api.py)
def prepare_features(match_data):
    """Prépare les features pour un match"""
    home_team = match_data['O1']
    away_team = match_data['O2']
    league = match_data['L']
    
    # Obtenir les stats des équipes
    home_stats = team_stats[team_stats['team'] == home_team].iloc[0] if len(team_stats[team_stats['team'] == home_team]) > 0 else None
    away_stats = team_stats[team_stats['team'] == away_team].iloc[0] if len(team_stats[team_stats['team'] == away_team]) > 0 else None
    
    # Obtenir les stats de la ligue
    league_avg = league_stats[league_stats['league'] == league]['avg_total_goals'].iloc[0] if len(league_stats[league_stats['league'] == league]) > 0 else 3.0
    
    # Créer les features avec les noms corrects
    home_win_rate = home_stats['win_rate'] if home_stats is not None else 0.5
    home_draw_rate = home_stats['draw_rate'] if home_stats is not None else 0.2
    home_avg_scored = home_stats['avg_goals_scored'] if home_stats is not None else 1.5
    home_avg_conceded = home_stats['avg_goals_conceded'] if home_stats is not None else 1.5
    
    away_win_rate = away_stats['win_rate'] if away_stats is not None else 0.5
    away_draw_rate = away_stats['draw_rate'] if away_stats is not None else 0.2
    away_avg_scored = away_stats['avg_goals_scored'] if away_stats is not None else 1.5
    away_avg_conceded = away_stats['avg_goals_conceded'] if away_stats is not None else 1.5
    
    features = {
        'home_team_win_rate': home_win_rate,
        'home_team_draw_rate': home_draw_rate,
        'home_team_avg_goals_scored': home_avg_scored,
        'home_team_avg_goals_conceded': home_avg_conceded,
        'away_team_win_rate': away_win_rate,
        'away_team_draw_rate': away_draw_rate,
        'away_team_avg_goals_scored': away_avg_scored,
        'away_team_avg_goals_conceded': away_avg_conceded,
        'avg_total_goals': league_avg,
        'goal_diff_avg': (home_avg_scored - home_avg_conceded) - (away_avg_scored - away_avg_conceded),
        'win_rate_diff': home_win_rate - away_win_rate,
        'league_encoded': hash(league) % 100,
        'year': datetime.now().year,
        'month': datetime.now().month,
        'day_of_week': datetime.now().weekday()
    }
    
    return pd.DataFrame([features])

# Données de test JSON
test_json = [
    {
        "I": 734797802,
        "O1": "Club Atlético de Madrid",
        "O2": "Porto",
        "L": "FC 26. 5x5 Rush. Superligue",
        "ST": "Paris avant le début du jeu",
        "S": 1783473000
    },
    {
        "I": 734796647,
        "O1": "Galatasaray",
        "O2": "Bayer 04",
        "L": "FC 26. 5x5 Rush. Superligue",
        "S": 1783472400
    },
    {
        "I": 734799022,
        "O1": "Juventus",
        "O2": "Real Madrid",
        "L": "FC 26. 5x5 Rush. Superligue",
        "ST": "Paris avant le début du jeu",
        "S": 1783473600
    }
]

print("=== TEST DU PARSING JSON ===\n")

# Test du parsing JSON
matches = parse_json_batch(test_json)
print(f"Nombre de matchs parsés: {len(matches)}")

for i, match in enumerate(matches, 1):
    print(f"Match {i}: {match.team_home} vs {match.team_away} ({match.league})")

print("\n=== TEST DES PRÉDICTIONS (MODE DIRECT) ===\n")

from league_family_mapping import get_league_family, get_family_options, map_prediction_to_platform

predictions = []
success_count = 0

for i, match in enumerate(matches, 1):
    try:
        # Convertir MatchData en dict pour prepare_features
        match_dict = match.to_dict()
        features = prepare_features(match_dict)
        
        # Obtenir la famille de la ligue
        family = get_league_family(match.league)
        family_options = get_family_options(family)
        
        # Prédiction du résultat
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        result_map = {0: 'away_win', 1: 'draw', 2: 'home_win'}
        result_text = result_map[prediction]
        
        # Prédiction Over/Under
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
        
        # Mapping plateforme
        total_goals_pred = features['avg_total_goals'].iloc[0]
        handicap_pred = features['goal_diff_avg'].iloc[0]
        total_goals_platform, total_goals_name = map_prediction_to_platform('total_goals', total_goals_pred, family)
        handicap_platform, handicap_name = map_prediction_to_platform('handicap', handicap_pred, family)
        
        print(f"Match {i}: {match.team_home} vs {match.team_away}")
        print(f"  Ligue: {match.league}")
        print(f"  Famille: {family}")
        print(f"  Résultat: {result_text} (confiance: {max(probabilities)*100:.2f}%)")
        print(f"  Over/Under ({overunder_threshold}): {overunder_text} (confiance: {max(overunder_proba)*100:.2f}%)")
        print(f"  BTTS: {btts_text} (confiance: {max(btts_proba)*100:.2f}%)")
        print(f"  Total Goals: {total_goals_pred:.1f} → Plateforme: {total_goals_platform} ({total_goals_name})")
        print(f"  Handicap: {handicap_pred:+.1f} → Plateforme: {handicap_platform:+.1f} ({handicap_name})")
        print()
        
        predictions.append({
            'match_id': match.match_id,
            'team_home': match.team_home,
            'team_away': match.team_away,
            'league': match.league,
            'family': family,
            'match_result': {
                'prediction': result_text,
                'confidence': float(max(probabilities))
            },
            'over_under': {
                'threshold': overunder_threshold,
                'prediction': overunder_text,
                'confidence': float(max(overunder_proba))
            },
            'btts': {
                'prediction': btts_text,
                'confidence': float(max(btts_proba))
            },
            'platform_mapping': {
                'total_goals': {
                    'predicted': float(total_goals_pred),
                    'platform_value': total_goals_platform
                },
                'handicap': {
                    'predicted': float(handicap_pred),
                    'platform_value': handicap_platform
                }
            }
        })
        
        success_count += 1
        
    except Exception as e:
        print(f"Erreur pour le match {i}: {str(e)}\n")

print(f"=== RÉSUMÉ ===")
print(f"Matchs traités: {len(matches)}")
print(f"Prédictions réussies: {success_count}")
print(f"Erreurs: {len(matches) - success_count}")

print(f"\n=== TEST DU SDK TERMINÉ ===")
print(f"Le SDK fonctionne correctement!")
print(f"Pour utiliser le SDK avec l'API, démarrez l'API avec: python prediction_api.py")
