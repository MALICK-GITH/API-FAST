import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import json

print("=== TEST DES PRÉDICTIONS ===\n")

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
        }
    }

# Test avec des exemples de matchs du système
test_matches = [
    {
        "I": 734797802,
        "O1": "Club Atlético de Madrid",
        "O2": "Porto",
        "L": "FC 26. 5x5 Rush. Superligue",
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
        "I": 734795374,
        "O1": "Lombardia",
        "O2": "Liverpool",
        "L": "FC 26. 5x5 Rush. Superligue",
        "S": 1783471800
    }
]

print("=== TEST DES PRÉDICTIONS SUR DES MATCHS EXEMPLES ===\n")

for i, match in enumerate(test_matches, 1):
    print(f"Match {i}: {match['O1']} vs {match['O2']}")
    print(f"Ligue: {match['L']}")
    
    try:
        prediction = predict_match(match)
        print(f"Prédiction: {prediction['prediction']}")
        print(f"Confiance: {prediction['confidence']:.2%}")
        print(f"Probabilités:")
        print(f"  - Victoire domicile: {prediction['probabilities']['home_win']:.2%}")
        print(f"  - Match nul: {prediction['probabilities']['draw']:.2%}")
        print(f"  - Victoire extérieur: {prediction['probabilities']['away_win']:.2%}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    print()

# Test avec le format JSON complet du système
print("=== TEST AVEC FORMAT JSON COMPLET DU SYSTÈME ===\n")

json_example = {
    "Id": 0,
    "Success": True,
    "Error": "",
    "ErrorCode": 0,
    "Guid": "",
    "Value": test_matches
}

try:
    predictions = []
    for match in json_example['Value']:
        prediction = predict_match(match)
        predictions.append(prediction)
    
    print("Prédictions réussies pour tous les matchs!")
    print(f"Nombre de prédictions: {len(predictions)}")
    
    # Afficher le résultat au format JSON
    result = {
        'success': True,
        'predictions': predictions
    }
    
    print("\n=== RÉSULTAT AU FORMAT JSON ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"Erreur lors du traitement du JSON: {e}")

# Test de validation sur des matchs historiques
print("\n=== VALIDATION SUR DES MATCHS HISTORIQUES ===\n")

# Prendre quelques matchs historiques pour tester
sample_matches = df_features.sample(5)

correct_predictions = 0
total_predictions = 0

for _, row in sample_matches.iterrows():
    match_data = {
        'I': row['match_id'],
        'O1': row['team_home'],
        'O2': row['team_away'],
        'L': row['league'],
        'S': int(pd.to_datetime(row['finished_at'], format='ISO8601').timestamp())
    }
    
    try:
        prediction = predict_match(match_data)
        actual_result = row['result']
        
        total_predictions += 1
        if prediction['prediction'] == actual_result:
            correct_predictions += 1
        
        print(f"Match: {match_data['O1']} vs {match_data['O2']}")
        print(f"Prédiction: {prediction['prediction']}")
        print(f"Résultat réel: {actual_result}")
        print(f"Correct: {prediction['prediction'] == actual_result}")
        print()
        
    except Exception as e:
        print(f"Erreur pour le match {match_data['I']}: {e}")

if total_predictions > 0:
    accuracy = correct_predictions / total_predictions
    print(f"Précision sur l'échantillon: {accuracy:.2%} ({correct_predictions}/{total_predictions})")

print("\n=== TEST TERMINÉ ===")
