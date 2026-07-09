"""
API de Prédiction FIFA par Ligues
==================================
API Flask pour les prédictions FIFA avec modèles par ligue

Author: SOLITAIRE HACK
Version: 2.0
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import warnings
from league_family_mapping import get_league_family, get_family_options, map_prediction_to_platform
from league_name_mapping import parse_platform_payload
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────
# CHARGEMENT DES MODÈLES PAR LIGUE
# ─────────────────────────────────────────

print("=== CHARGEMENT DES MODÈLES PAR LIGUE ===\n")

models_dir = 'models_by_league'
models_by_league = {}

# Charger les stats des équipes
print("Chargement des statistiques des équipes...")
team_stats = pd.read_csv('team_stats_fifa.csv')
print(f"Stats des équipes chargées: {len(team_stats)} équipes")

# Charger les stats des ligues
league_stats = pd.read_csv('training_features_fifa.csv')[['league', 'avg_total_goals']].drop_duplicates()
print(f"Stats des ligues chargées: {len(league_stats)} ligues")

# Charger tous les modèles par ligue
print("\nChargement des modèles par ligue...")
for filename in os.listdir(models_dir):
    if filename.endswith('_result.pkl'):
        league_name = filename.replace('_result.pkl', '').replace('_', ' ')
        try:
            model_path = os.path.join(models_dir, filename)
            features_path = os.path.join(models_dir, filename.replace('_result.pkl', '_result_features.pkl'))
            
            if os.path.exists(model_path) and os.path.exists(features_path):
                model = joblib.load(model_path)
                features = joblib.load(features_path)
                
                league_key = filename.replace('_result.pkl', '')
                models_by_league[league_key] = {
                    'result_model': model,
                    'result_features': features
                }
                print(f"  [OK] {league_name}")
        except Exception as e:
            print(f"  [ERROR] Erreur chargement {filename}: {e}")

# Charger les modèles de buts et parité
for league_key in models_by_league.keys():
    try:
        goals_model_path = os.path.join(models_dir, f'{league_key}_goals.pkl')
        goals_features_path = os.path.join(models_dir, f'{league_key}_goals_features.pkl')
        parity_model_path = os.path.join(models_dir, f'{league_key}_parity.pkl')
        parity_features_path = os.path.join(models_dir, f'{league_key}_parity_features.pkl')
        
        if os.path.exists(goals_model_path) and os.path.exists(goals_features_path):
            models_by_league[league_key]['goals_model'] = joblib.load(goals_model_path)
            models_by_league[league_key]['goals_features'] = joblib.load(goals_features_path)
        
        if os.path.exists(parity_model_path) and os.path.exists(parity_features_path):
            models_by_league[league_key]['parity_model'] = joblib.load(parity_model_path)
            models_by_league[league_key]['parity_features'] = joblib.load(parity_features_path)
    except Exception as e:
        print(f"  ✗ Erreur chargement modèles secondaires pour {league_key}: {e}")

print(f"\nModèles chargés: {len(models_by_league)} ligues")

# ─────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────

def get_league_key(league_name):
    """Convertit le nom de ligue en clé pour les modèles"""
    return league_name.replace(' ', '_').replace('.', '_').replace('/', '_')

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
    
    # Créer les features
    home_win_rate = home_stats['win_rate'] if home_stats is not None else 0.5
    home_draw_rate = home_stats['draw_rate'] if home_stats is not None else 0.2
    home_avg_scored = home_stats['avg_goals_scored'] if home_stats is not None else 1.5
    home_avg_conceded = home_stats['avg_goals_conceded'] if home_stats is not None else 1.5
    
    away_win_rate = away_stats['win_rate'] if away_stats is not None else 0.5
    away_draw_rate = away_stats['draw_rate'] if away_stats is not None else 0.2
    away_avg_scored = away_stats['avg_goals_scored'] if away_stats is not None else 1.5
    away_avg_conceded = away_stats['avg_goals_conceded'] if away_stats is not None else 1.5
    
    features = {
        'home_win_rate': home_win_rate,
        'home_draw_rate': home_draw_rate,
        'home_avg_goals_scored': home_avg_scored,
        'home_avg_goals_conceded': home_avg_conceded,
        'away_win_rate': away_win_rate,
        'away_draw_rate': away_draw_rate,
        'away_avg_goals_scored': away_avg_scored,
        'away_avg_goals_conceded': away_avg_conceded,
        'avg_total_goals': league_avg,
        'goal_diff_avg': (home_avg_scored - home_avg_conceded) - (away_avg_scored - away_avg_conceded),
        'win_rate_diff': home_win_rate - away_win_rate,
        'league_encoded': hash(league) % 100,
        'year': datetime.now().year,
        'month': datetime.now().month,
        'day_of_week': datetime.now().weekday(),
        'h2h_home_wins': 0.5,
        'h2h_avg_goals': league_avg,
        'h2h_n': 0
    }
    
    return pd.DataFrame([features])

def predict_match(match_data):
    """Prédit le résultat d'un match avec les modèles par ligue"""
    try:
        # Préparer les features
        features = prepare_features(match_data)
        
        # Obtenir la ligue et sa clé
        league = match_data['L']
        league_key = get_league_key(league)
        
        # Obtenir la famille de la ligue
        family = get_league_family(league)
        family_options = get_family_options(family)
        
        # Vérifier si le modèle existe pour cette ligue
        if league_key not in models_by_league:
            return {
                'error': f'Modèle non disponible pour la ligue: {league}',
                'match_id': match_data.get('I', 'unknown'),
                'available_leagues': list(models_by_league.keys())
            }
        
        league_models = models_by_league[league_key]
        
        # ─── PRÉDICTION VICTOIRES ───
        result_features = features[league_models['result_features']]
        result_pred = league_models['result_model'].predict(result_features)[0]
        result_proba = league_models['result_model'].predict_proba(result_features)[0]
        result_map = {0: 'away_win', 1: 'draw', 2: 'home_win'}
        result_text = result_map[result_pred]
        
        # ─── PRÉDICTION TOTAL BUTS ───
        if 'goals_model' in league_models:
            goals_features = features[league_models['goals_features']]
            goals_pred = league_models['goals_model'].predict(goals_features)[0]
        else:
            goals_pred = features['avg_total_goals'].iloc[0]
        
        # ─── PRÉDICTION PARITÉ ───
        if 'parity_model' in league_models:
            parity_features = features[league_models['parity_features']]
            parity_pred = league_models['parity_model'].predict(parity_features)[0]
            parity_proba = league_models['parity_model'].predict_proba(parity_features)[0]
            parity_text = 'even' if parity_pred == 0 else 'odd'
        else:
            parity_text = 'even' if int(goals_pred) % 2 == 0 else 'odd'
            parity_proba = [0.5, 0.5]
        
        # ─── MAPPING PLATEFORME ───
        total_goals_platform, total_goals_name = map_prediction_to_platform('total_goals', goals_pred, family)
        handicap_pred = features['goal_diff_avg'].iloc[0]
        handicap_platform, handicap_name = map_prediction_to_platform('handicap', handicap_pred, family)
        
        # ─── OVER/UNDER (basé sur le seuil de la famille) ───
        overunder_threshold = family_options['over_under_threshold']
        overunder_text = 'over' if goals_pred > overunder_threshold else 'under'
        
        # Créer le résultat
        result = {
            'success': True,
            'match_id': match_data.get('I', 'unknown'),
            'team_home': match_data['O1'],
            'team_away': match_data['O2'],
            'league': league,
            'family': family,
            'predictions': {
                'match_result': {
                    'prediction': result_text,
                    'confidence': float(max(result_proba)),
                    'probabilities': {
                        'away_win': float(result_proba[0]),
                        'draw': float(result_proba[1]),
                        'home_win': float(result_proba[2])
                    }
                },
                'total_goals': {
                    'predicted': float(goals_pred),
                    'platform_value': total_goals_platform,
                    'confidence': 0.7  # Estimation
                },
                'total_parity': {
                    'prediction': parity_text,
                    'confidence': float(max(parity_proba))
                },
                'over_under': {
                    'threshold': overunder_threshold,
                    'prediction': overunder_text,
                    'confidence': 0.7  # Estimation
                }
            },
            'platform_mapping': {
                'total_goals': {
                    'predicted': float(goals_pred),
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
            'success': False,
            'error': str(e),
            'match_id': match_data.get('I', 'unknown')
        }

# ─────────────────────────────────────────
# ENDPOINTS API
# ─────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health_check():
    """Vérifie la santé de l'API"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(models_by_league),
        'leagues_supported': list(models_by_league.keys()),
        'teams_in_stats': len(team_stats)
    })

@app.route('/leagues', methods=['GET'])
def get_leagues():
    """Retourne la liste des ligues supportées"""
    leagues_info = []
    for league_key, models in models_by_league.items():
        leagues_info.append({
            'name': league_key.replace('_', ' '),
            'key': league_key,
            'models': {
                'result': 'result_model' in models,
                'goals': 'goals_model' in models,
                'parity': 'parity_model' in models
            }
        })
    
    return jsonify({
        'total': len(leagues_info),
        'leagues': leagues_info
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Prédiction pour un match"""
    data = request.json
    
    # Normaliser le payload de la plateforme
    normalized_data = parse_platform_payload(data)
    
    result = predict_match(normalized_data)
    return jsonify(result)

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Prédictions pour plusieurs matchs"""
    data = request.json
    matches = data.get('matches', [])
    
    predictions = []
    for match in matches:
        # Normaliser le payload de la plateforme pour chaque match
        normalized_match = parse_platform_payload(match)
        result = predict_match(normalized_match)
        predictions.append(result)
    
    return jsonify({
        'success': True,
        'total': len(predictions),
        'predictions': predictions
    })

@app.route('/model/<league_name>', methods=['GET'])
def get_model_info(league_name):
    """Informations sur le modèle d'une ligue"""
    league_key = get_league_key(league_name)
    
    if league_key not in models_by_league:
        return jsonify({
            'error': f'Modèle non trouvé pour la ligue: {league_name}'
        }), 404
    
    models = models_by_league[league_key]
    
    return jsonify({
        'league': league_name,
        'key': league_key,
        'models': {
            'result': 'result_model' in models,
            'goals': 'goals_model' in models,
            'parity': 'parity_model' in models
        }
    })

if __name__ == '__main__':
    print("\n=== API FLASK DÉMARRÉE ===")
    print("Endpoints disponibles:")
    print("  - GET  /health")
    print("  - GET  /leagues")
    print("  - POST /predict")
    print("  - POST /predict/batch")
    print("  - GET  /model/<league_name>")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
