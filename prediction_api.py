import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import warnings
from league_family_mapping import get_league_family, get_family_options, map_prediction_to_platform
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Charger les modèles et les features
print("Chargement des modèles...")
model = joblib.load('fifa_prediction_model.pkl')
feature_columns = joblib.load('feature_columns.pkl')
overunder_model = joblib.load('overunder_model.pkl')
overunder_feature_columns = joblib.load('overunder_feature_columns.pkl')
btts_model = joblib.load('btts_model.pkl')
btts_feature_columns = joblib.load('btts_feature_columns.pkl')
team_stats = pd.read_csv('team_stats.csv')
league_stats = pd.read_csv('training_features.csv')[['league', 'avg_total_goals']].drop_duplicates()

print("Modèles chargés avec succès!")

def get_team_stats(team_name):
    """Récupère les statistiques d'une équipe"""
    stats = team_stats[team_stats['team'] == team_name]
    if len(stats) > 0:
        return stats.iloc[0].to_dict()
    else:
        # Retourner des statistiques par défaut si l'équipe n'est pas trouvée
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
        return 3.0  # Moyenne par défaut

def prepare_features(match_data):
    """Prépare les features pour la prédiction"""
    # Extraire les données du match
    team_home = match_data['O1']
    team_away = match_data['O2']
    league = match_data['L']
    
    # Obtenir les statistiques des équipes
    home_stats = get_team_stats(team_home)
    away_stats = get_team_stats(team_away)
    
    # Obtenir les statistiques de la ligue
    avg_total_goals = get_league_stats(league)
    
    # Calculer les différences
    goal_diff_avg = home_stats['avg_goals_scored'] - away_stats['avg_goals_scored']
    win_rate_diff = home_stats['win_rate'] - away_stats['win_rate']
    
    # Encoder la ligue (top 20 ligues)
    top_leagues = league_stats['league'].value_counts().head(20).index.tolist()
    league_encoded = 1 if league in top_leagues else 0
    
    # Extraire la date du timestamp
    timestamp = match_data.get('S', datetime.now().timestamp())
    date = datetime.fromtimestamp(timestamp)
    
    # Créer le dataframe de features
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
    """Prédit le résultat d'un match avec Over/Under et BTTS"""
    try:
        # Préparer les features
        features = prepare_features(match_data)
        
        # Obtenir la famille de la ligue
        league = match_data['L']
        family = get_league_family(league)
        family_options = get_family_options(family)
        
        # Prédiction du résultat du match
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Convertir la prédiction en texte
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
        
        # Créer le résultat
        result = {
            'match_id': match_data.get('I', 'unknown'),
            'team_home': match_data['O1'],
            'team_away': match_data['O2'],
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
            'timestamp': match_data.get('S', datetime.now().timestamp())
        }
        
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'match_id': match_data.get('I', 'unknown')
        }

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint de prédiction pour un match"""
    try:
        data = request.json
        
        # Vérifier si les données sont dans le format attendu
        if 'Value' in data:
            matches = data['Value']
        else:
            matches = [data]
        
        predictions = []
        for match in matches:
            prediction = predict_match(match)
            predictions.append(prediction)
        
        return jsonify({
            'success': True,
            'predictions': predictions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """Endpoint de prédiction pour plusieurs matchs"""
    try:
        data = request.json
        matches = data.get('matches', [])
        
        predictions = []
        for match in matches:
            prediction = predict_match(match)
            predictions.append(prediction)
        
        return jsonify({
            'success': True,
            'predictions': predictions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': {
            'match_result': model is not None,
            'over_under': overunder_model is not None,
            'btts': btts_model is not None
        },
        'feature_columns': {
            'match_result': len(feature_columns),
            'over_under': len(overunder_feature_columns),
            'btts': len(btts_feature_columns)
        }
    })

@app.route('/team_stats/<team_name>', methods=['GET'])
def get_team_stats_endpoint(team_name):
    """Endpoint pour obtenir les statistiques d'une équipe"""
    stats = get_team_stats(team_name)
    return jsonify(stats)

if __name__ == '__main__':
    print("\n=== API DE PRÉDICTION FIFA ===")
    print("Démarrage du serveur...")
    print("Endpoints disponibles:")
    print("  POST /predict - Prédire un ou plusieurs matchs")
    print("  POST /predict_batch - Prédire plusieurs matchs")
    print("  GET /health - Vérifier la santé de l'API")
    print("  GET /team_stats/<team_name> - Obtenir les statistiques d'une équipe")
    print("\nLe serveur sera accessible sur http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
