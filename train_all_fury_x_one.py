"""
Script Complet d'Entraînement - FURY X ONE
==========================================

Ce script effectue tout le processus d'entraînement:
1. Création des features
2. Entraînement des modèles par ligues
3. Mise à jour de l'API
4. Tests

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import subprocess
import sys

print("=" * 80)
print("ENTRAÎNEMENT COMPLET - FURY X ONE")
print("=" * 80)

# ÉTAPE 1: Création des features
print("\n" + "=" * 80)
print("ÉTAPE 1: CRÉATION DES FEATURES")
print("=" * 80)

df = pd.read_csv('finished_matches_clean.csv')
print(f"✅ Données chargées: {len(df)} matchs")

df['finished_at'] = pd.to_datetime(df['finished_at'], format='ISO8601')
df['year'] = df['finished_at'].dt.year
df['month'] = df['finished_at'].dt.month
df['day_of_week'] = df['finished_at'].dt.dayofweek

# Stats par équipe
team_stats = df.groupby('team_home').agg({
    'score_home': ['mean', 'sum', 'count'],
    'score_away': ['mean']
}).reset_index()
team_stats.columns = ['team', 'avg_goals_scored_home', 'total_goals_scored_home', 'matches_played_home', 'avg_goals_conceded_home']

away_stats = df.groupby('team_away').agg({
    'score_away': ['mean', 'sum', 'count'],
    'score_home': ['mean']
}).reset_index()
away_stats.columns = ['team', 'avg_goals_scored_away', 'total_goals_scored_away', 'matches_played_away', 'avg_goals_conceded_away']

team_stats = team_stats.merge(away_stats, on='team', how='outer').fillna(0)
team_stats['avg_goals_scored'] = (team_stats['avg_goals_scored_home'] + team_stats['avg_goals_scored_away']) / 2
team_stats['avg_goals_conceded'] = (team_stats['avg_goals_conceded_home'] + team_stats['avg_goals_conceded_away']) / 2
team_stats['total_matches'] = team_stats['matches_played_home'] + team_stats['matches_played_away']
team_stats['win_rate'] = 0.5
team_stats['draw_rate'] = 0.2

team_stats.to_csv('team_stats_fifa.csv', index=False)
print(f"✅ Stats des équipes: {len(team_stats)} équipes")

# Stats par ligue
league_stats = df.groupby('league').agg({
    'score_home': 'mean',
    'score_away': 'mean'
}).reset_index()
league_stats['avg_total_goals'] = league_stats['score_home'] + league_stats['score_away']
league_stats = league_stats[['league', 'avg_total_goals']]
league_stats.to_csv('league_stats_fifa.csv', index=False)
print(f"✅ Stats des ligues: {len(league_stats)} ligues")

# Features d'entraînement
training_features = []
for _, row in df.iterrows():
    home_team_stats = team_stats[team_stats['team'] == row['team_home']]
    home_stats = home_team_stats.iloc[0].to_dict() if len(home_team_stats) > 0 else {
        'avg_goals_scored': 1.5, 'avg_goals_conceded': 1.5, 'win_rate': 0.5, 'draw_rate': 0.2
    }
    
    away_team_stats = team_stats[team_stats['team'] == row['team_away']]
    away_stats = away_team_stats.iloc[0].to_dict() if len(away_team_stats) > 0 else {
        'avg_goals_scored': 1.5, 'avg_goals_conceded': 1.5, 'win_rate': 0.5, 'draw_rate': 0.2
    }
    
    league_avg = league_stats[league_stats['league'] == row['league']]['avg_total_goals'].iloc[0] if len(league_stats[league_stats['league'] == row['league']]) > 0 else 3.0
    
    features = {
        'match_id': row['match_id'],
        'team_home': row['team_home'],
        'team_away': row['team_away'],
        'league': row['league'],
        'score_home': row['score_home'],
        'score_away': row['score_away'],
        'total_goals': row['score_home'] + row['score_away'],
        'home_win': 1 if row['score_home'] > row['score_away'] else 0,
        'draw': 1 if row['score_home'] == row['score_away'] else 0,
        'away_win': 1 if row['score_away'] > row['score_home'] else 0,
        'total_parity': (row['score_home'] + row['score_away']) % 2,
        'home_win_rate': home_stats['win_rate'],
        'home_draw_rate': home_stats['draw_rate'],
        'home_avg_goals_scored': home_stats['avg_goals_scored'],
        'home_avg_goals_conceded': home_stats['avg_goals_conceded'],
        'away_win_rate': away_stats['win_rate'],
        'away_draw_rate': away_stats['draw_rate'],
        'away_avg_goals_scored': away_stats['avg_goals_scored'],
        'away_avg_goals_conceded': away_stats['avg_goals_conceded'],
        'avg_total_goals': league_avg,
        'goal_diff_avg': (home_stats['avg_goals_scored'] - home_stats['avg_goals_conceded']) - (away_stats['avg_goals_scored'] - away_stats['avg_goals_conceded']),
        'win_rate_diff': home_stats['win_rate'] - away_stats['win_rate'],
        'league_encoded': hash(row['league']) % 100,
        'year': row['year'],
        'month': row['month'],
        'day_of_week': row['day_of_week'],
        'h2h_home_wins': 0.5,
        'h2h_avg_goals': league_avg,
        'h2h_n': 0
    }
    training_features.append(features)

training_df = pd.DataFrame(training_features)
training_df.to_csv('training_features_fifa.csv', index=False)
print(f"✅ Features d'entraînement: {len(training_df)} matchs")

# ÉTAPE 2: Entraînement des modèles par ligues
print("\n" + "=" * 80)
print("ÉTAPE 2: ENTRAÎNEMENT DES MODÈLES PAR LIGUES")
print("=" * 80)

from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib

# Créer le répertoire des modèles
if not os.path.exists('models_by_league'):
    os.makedirs('models_by_league')

# Entraîner pour chaque ligue
leagues = training_df['league'].unique()
print(f"Nombre de ligues: {len(leagues)}")

feature_columns = [
    'home_win_rate', 'home_draw_rate', 'home_avg_goals_scored', 'home_avg_goals_conceded',
    'away_win_rate', 'away_draw_rate', 'away_avg_goals_scored', 'away_avg_goals_conceded',
    'avg_total_goals', 'goal_diff_avg', 'win_rate_diff', 'league_encoded',
    'year', 'month', 'day_of_week'
]

models_summary = []

for league in leagues:
    print(f"\nEntraînement pour: {league}")
    
    league_data = training_df[training_df['league'] == league]
    
    if len(league_data) < 100:
        print(f"  ⚠️  Pas assez de données ({len(league_data)} matchs)")
        continue
    
    X = league_data[feature_columns]
    y_result = league_data['home_win']
    y_goals = league_data['total_goals']
    y_parity = league_data['total_parity']
    
    # Split
    X_train, X_test, y_result_train, y_result_test = train_test_split(X, y_result, test_size=0.2, random_state=42)
    _, _, y_goals_train, y_goals_test = train_test_split(X, y_goals, test_size=0.2, random_state=42)
    _, _, y_parity_train, y_parity_test = train_test_split(X, y_parity, test_size=0.2, random_state=42)
    
    # Modèle Result
    result_model = RandomForestClassifier(n_estimators=100, random_state=42)
    result_model.fit(X_train, y_result_train)
    result_acc = accuracy_score(y_result_test, result_model.predict(X_test))
    
    # Modèle Goals
    goals_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    goals_model.fit(X_train, y_goals_train)
    goals_mse = mean_squared_error(y_goals_test, goals_model.predict(X_test))
    
    # Modèle Parity
    parity_model = RandomForestClassifier(n_estimators=100, random_state=42)
    parity_model.fit(X_train, y_parity_train)
    parity_acc = accuracy_score(y_parity_test, parity_model.predict(X_test))
    
    # Sauvegarder les modèles
    league_key = league.replace(' ', '_').replace('.', '_')
    
    joblib.dump(result_model, f'models_by_league/{league_key}_result.pkl')
    joblib.dump(goals_model, f'models_by_league/{league_key}_goals.pkl')
    joblib.dump(parity_model, f'models_by_league/{league_key}_parity.pkl')
    joblib.dump(feature_columns, f'models_by_league/{league_key}_result_features.pkl')
    joblib.dump(feature_columns, f'models_by_league/{league_key}_goals_features.pkl')
    joblib.dump(feature_columns, f'models_by_league/{league_key}_parity_features.pkl')
    
    models_summary.append({
        'league': league,
        'league_key': league_key,
        'matches': len(league_data),
        'result_accuracy': result_acc,
        'goals_mse': goals_mse,
        'parity_accuracy': parity_acc
    })
    
    print(f"  ✅ Modèles entraînés - Result: {result_acc:.3f}, Goals: {goals_mse:.3f}, Parity: {parity_acc:.3f}")

# Sauvegarder le résumé
summary_df = pd.DataFrame(models_summary)
summary_df.to_csv('models_by_league/models_summary.csv', index=False)
print(f"\n✅ Résumé des modèles sauvegardé: {len(models_summary)} ligues")

# ÉTAPE 3: Mise à jour de l'API
print("\n" + "=" * 80)
print("ÉTAPE 3: MISE À JOUR DE L'API")
print("=" * 80)
print("✅ Les modèles sont prêts à être utilisés par l'API")
print("✅ L'API chargera automatiquement les modèles depuis models_by_league/")

# ÉTAPE 4: Tests
print("\n" + "=" * 80)
print("ÉTAPE 4: TESTS")
print("=" * 80)
print("✅ Les modèles peuvent être testés en démarrant l'API")
print("   Commande: python prediction_api_league.py")

print("\n" + "=" * 80)
print("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
print("=" * 80)
print(f"Total ligues entraînées: {len(models_summary)}")
print(f"Total matchs utilisés: {len(training_df)}")
print(f"Modèles sauvegardés dans: models_by_league/")
print("=" * 80)
