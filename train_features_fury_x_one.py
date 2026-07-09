"""
Création des Features d'Entraînement - FURY X ONE
================================================

Ce script génère les features d'entraînement à partir des données de matchs
en utilisant le mapping officiel FURY X ONE des ligues EA SPORTS FC.

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

print("=" * 80)
print("CRÉATION DES FEATURES D'ENTRAÎNEMENT - FURY X ONE")
print("=" * 80)

# Charger les données
print("\nChargement des données...")
df = pd.read_csv('finished_matches_clean.csv')
print(f"✅ Données chargées: {len(df)} matchs")

# Convertir les dates
df['finished_at'] = pd.to_datetime(df['finished_at'])
df['year'] = df['finished_at'].dt.year
df['month'] = df['finished_at'].dt.month
df['day_of_week'] = df['finished_at'].dt.dayofweek

# Calculer les features par équipe
print("\nCalcul des statistiques par équipe...")
team_stats = df.groupby('team_home').agg({
    'score_home': ['mean', 'sum', 'count'],
    'score_away': ['mean']
}).reset_index()
team_stats.columns = ['team', 'avg_goals_scored_home', 'total_goals_scored_home', 'matches_played_home', 'avg_goals_conceded_home']

# Stats pour les équipes à l'extérieur
away_stats = df.groupby('team_away').agg({
    'score_away': ['mean', 'sum', 'count'],
    'score_home': ['mean']
}).reset_index()
away_stats.columns = ['team', 'avg_goals_scored_away', 'total_goals_scored_away', 'matches_played_away', 'avg_goals_conceded_away']

# Fusionner les stats
team_stats = team_stats.merge(away_stats, on='team', how='outer').fillna(0)

# Calculer les stats globales
team_stats['avg_goals_scored'] = (team_stats['avg_goals_scored_home'] + team_stats['avg_goals_scored_away']) / 2
team_stats['avg_goals_conceded'] = (team_stats['avg_goals_conceded_home'] + team_stats['avg_goals_conceded_away']) / 2
team_stats['total_matches'] = team_stats['matches_played_home'] + team_stats['matches_played_away']
team_stats['win_rate'] = 0.5  # Placeholder
team_stats['draw_rate'] = 0.2  # Placeholder

# Sauvegarder les stats des équipes
team_stats.to_csv('team_stats_fifa.csv', index=False)
print(f"✅ Stats des équipes sauvegardées: {len(team_stats)} équipes")

# Calculer les features par ligue
print("\nCalcul des statistiques par ligue...")
league_stats = df.groupby('league').agg({
    'score_home': 'mean',
    'score_away': 'mean'
}).reset_index()
league_stats['avg_total_goals'] = league_stats['score_home'] + league_stats['score_away']
league_stats = league_stats[['league', 'avg_total_goals']]

# Sauvegarder les stats des ligues
league_stats.to_csv('league_stats_fifa.csv', index=False)
print(f"✅ Stats des ligues sauvegardées: {len(league_stats)} ligues")

# Créer les features d'entraînement
print("\nCréation des features d'entraînement...")
training_features = []

for _, row in df.iterrows():
    # Obtenir les stats de l'équipe domicile
    home_team_stats = team_stats[team_stats['team'] == row['team_home']]
    if len(home_team_stats) > 0:
        home_stats = home_team_stats.iloc[0]
    else:
        home_stats = {
            'avg_goals_scored': 1.5,
            'avg_goals_conceded': 1.5,
            'win_rate': 0.5,
            'draw_rate': 0.2
        }
    
    # Obtenir les stats de l'équipe extérieur
    away_team_stats = team_stats[team_stats['team'] == row['team_away']]
    if len(away_team_stats) > 0:
        away_stats = away_team_stats.iloc[0]
    else:
        away_stats = {
            'avg_goals_scored': 1.5,
            'avg_goals_conceded': 1.5,
            'win_rate': 0.5,
            'draw_rate': 0.2
        }
    
    # Obtenir les stats de la ligue
    league_avg = league_stats[league_stats['league'] == row['league']]['avg_total_goals'].iloc[0] if len(league_stats[league_stats['league'] == row['league']]) > 0 else 3.0
    
    # Créer les features
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
        'h2h_home_wins': 0.5,  # Placeholder
        'h2h_avg_goals': league_avg,
        'h2h_n': 0
    }
    
    training_features.append(features)

# Créer le DataFrame
training_df = pd.DataFrame(training_features)
training_df.to_csv('training_features_fifa.csv', index=False)
print(f"✅ Features d'entraînement sauvegardées: {len(training_df)} matchs")

# Afficher les statistiques
print("\n" + "=" * 80)
print("STATISTIQUES DES FEATURES")
print("=" * 80)
print(f"Total matchs: {len(training_df)}")
print(f"Total ligues: {training_df['league'].nunique()}")
print(f"Total équipes: {training_df['team_home'].nunique()}")
print(f"\nRépartition des résultats:")
print(f"Victoires domicile: {training_df['home_win'].sum()}")
print(f"Matchs nuls: {training_df['draw'].sum()}")
print(f"Victoires extérieur: {training_df['away_win'].sum()}")
print(f"\nMoyenne des buts totaux: {training_df['total_goals'].mean():.2f}")
print(f"\nLigues:")
print(training_df['league'].value_counts())

print("\n" + "=" * 80)
print("✅ FEATURES D'ENTRAÎNEMENT CRÉÉES AVEC SUCCÈS")
print("=" * 80)
