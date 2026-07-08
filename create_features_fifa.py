"""
Création des Features pour les Ligues FIFA
===========================================
Script pour créer les features d'entraînement à partir du dataset FIFA filtré

Author: SOLITAIRE HACK
Version: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=== CRÉATION DES FEATURES POUR LES LIGUES FIFA ===\n")

# Charger le dataset FIFA filtré
print("Chargement du dataset FIFA...")
df = pd.read_csv('finished_matches_clean.csv')
print(f"Dataset chargé: {len(df):,} matchs")

# Convertir les dates
df['finished_at'] = pd.to_datetime(df['finished_at'], format='ISO8601')
df['year'] = df['finished_at'].dt.year
df['month'] = df['finished_at'].dt.month
df['day_of_week'] = df['finished_at'].dt.dayofweek

# Calculer les statistiques par équipe
print("\nCalcul des statistiques par équipe...")
team_stats = df.groupby('team_home').agg({
    'score_home': ['mean', 'sum', 'count'],
    'score_away': ['mean']
}).reset_index()
team_stats.columns = ['team', 'avg_goals_scored', 'total_goals_scored', 'matches_played', 'avg_goals_conceded_home']

# Calculer les stats en tant qu'équipe extérieur
away_stats = df.groupby('team_away').agg({
    'score_away': ['mean', 'sum', 'count'],
    'score_home': ['mean']
}).reset_index()
away_stats.columns = ['team', 'avg_goals_scored_away', 'total_goals_scored_away', 'matches_played_away', 'avg_goals_conceded_away']

# Fusionner les stats
team_stats_full = team_stats.merge(away_stats, on='team', how='outer').fillna(0)

# Calculer les stats finales
team_stats_full['avg_goals_scored'] = (team_stats_full['avg_goals_scored'] + team_stats_full['avg_goals_scored_away']) / 2
team_stats_full['avg_goals_conceded'] = (team_stats_full['avg_goals_conceded_home'] + team_stats_full['avg_goals_conceded_away']) / 2
team_stats_full['matches_played'] = team_stats_full['matches_played'] + team_stats_full['matches_played_away']

# Calculer le win rate
df['home_win'] = (df['score_home'] > df['score_away']).astype(int)
df['away_win'] = (df['score_away'] > df['score_home']).astype(int)
df['draw'] = (df['score_home'] == df['score_away']).astype(int)

home_wins = df.groupby('team_home')['home_win'].sum().reset_index()
away_wins = df.groupby('team_away')['away_win'].sum().reset_index()
draws_home = df.groupby('team_home')['draw'].sum().reset_index()
draws_away = df.groupby('team_away')['draw'].sum().reset_index()

home_wins.columns = ['team', 'home_wins']
away_wins.columns = ['team', 'away_wins']
draws_home.columns = ['team', 'draws_home']
draws_away.columns = ['team', 'draws_away']

team_stats_full = team_stats_full.merge(home_wins, on='team', how='left').fillna(0)
team_stats_full = team_stats_full.merge(away_wins, on='team', how='left').fillna(0)
team_stats_full = team_stats_full.merge(draws_home, on='team', how='left').fillna(0)
team_stats_full = team_stats_full.merge(draws_away, on='team', how='left').fillna(0)

team_stats_full['total_wins'] = team_stats_full['home_wins'] + team_stats_full['away_wins']
team_stats_full['total_draws'] = team_stats_full['draws_home'] + team_stats_full['draws_away']
team_stats_full['win_rate'] = team_stats_full['total_wins'] / team_stats_full['matches_played']
team_stats_full['draw_rate'] = team_stats_full['total_draws'] / team_stats_full['matches_played']

# Sélectionner les colonnes finales
team_stats_final = team_stats_full[['team', 'win_rate', 'draw_rate', 'avg_goals_scored', 'avg_goals_conceded', 'matches_played']]

# Sauvegarder les stats des équipes
team_stats_final.to_csv('team_stats_fifa.csv', index=False)
print(f"Statistiques des équipes sauvegardées: team_stats_fifa.csv ({len(team_stats_final)} équipes)")

# Calculer les statistiques par ligue
print("\nCalcul des statistiques par ligue...")
league_stats = df.groupby('league').agg({
    'score_home': ['mean', 'sum'],
    'score_away': ['mean', 'sum'],
    'match_id': 'count'
}).reset_index()
league_stats.columns = ['league', 'avg_home_scored', 'total_home_scored', 'avg_away_scored', 'total_away_scored', 'total_matches']
league_stats['avg_total_goals'] = league_stats['avg_home_scored'] + league_stats['avg_away_scored']

print(f"Statistiques des ligues calculées: {len(league_stats)} ligues")

# Créer les features pour chaque match
print("\nCréation des features pour chaque match...")

def get_team_stats(team_name, stats_df):
    """Récupère les stats d'une équipe"""
    team_row = stats_df[stats_df['team'] == team_name]
    if len(team_row) > 0:
        return team_row.iloc[0]
    else:
        return pd.Series({'win_rate': 0.5, 'draw_rate': 0.2, 'avg_goals_scored': 1.5, 'avg_goals_conceded': 1.5, 'matches_played': 0})

def get_league_avg(league_name, stats_df):
    """Récupère la moyenne de buts d'une ligue"""
    league_row = stats_df[stats_df['league'] == league_name]
    if len(league_row) > 0:
        return league_row.iloc[0]['avg_total_goals']
    else:
        return 3.0

# Fusionner les stats des équipes
df = df.merge(team_stats_final.add_prefix('home_'), left_on='team_home', right_on='home_team', how='left')
df = df.merge(team_stats_final.add_prefix('away_'), left_on='team_away', right_on='away_team', how='left')
df = df.merge(league_stats[['league', 'avg_total_goals']], on='league', how='left')

# Remplir les valeurs manquantes
df['home_win_rate'] = df['home_win_rate'].fillna(0.5)
df['home_draw_rate'] = df['home_draw_rate'].fillna(0.2)
df['home_avg_goals_scored'] = df['home_avg_goals_scored'].fillna(1.5)
df['home_avg_goals_conceded'] = df['home_avg_goals_conceded'].fillna(1.5)

df['away_win_rate'] = df['away_win_rate'].fillna(0.5)
df['away_draw_rate'] = df['away_draw_rate'].fillna(0.2)
df['away_avg_goals_scored'] = df['away_avg_goals_scored'].fillna(1.5)
df['away_avg_goals_conceded'] = df['away_avg_goals_conceded'].fillna(1.5)

df['avg_total_goals'] = df['avg_total_goals'].fillna(3.0)

# Encoder la ligue
df['league_encoded'] = df['league'].astype('category').cat.codes

# Calculer les features dérivées
df['goal_diff_avg'] = (df['home_avg_goals_scored'] - df['home_avg_goals_conceded']) - (df['away_avg_goals_scored'] - df['away_avg_goals_conceded'])
df['win_rate_diff'] = df['home_win_rate'] - df['away_win_rate']

# Calculer les stats H2H (head-to-head)
print("Calcul des stats H2H...")
def calculate_h2h(home_team, away_team, df_full):
    """Calcule les stats tête-à-tête entre deux équipes"""
    h2h_matches = df_full[((df_full['team_home'] == home_team) & (df_full['team_away'] == away_team)) |
                         ((df_full['team_home'] == away_team) & (df_full['team_away'] == home_team))]
    
    if len(h2h_matches) == 0:
        return pd.Series({'h2h_home_wins': 0.5, 'h2h_avg_goals': 2.5, 'h2h_n': 0})
    
    home_wins_h2h = len(h2h_matches[(h2h_matches['team_home'] == home_team) & (h2h_matches['score_home'] > h2h_matches['score_away'])]) + \
                   len(h2h_matches[(h2h_matches['team_away'] == home_team) & (h2h_matches['score_away'] > h2h_matches['score_home'])])
    
    avg_goals_h2h = (h2h_matches['score_home'] + h2h_matches['score_away']).mean()
    
    return pd.Series({
        'h2h_home_wins': home_wins_h2h / len(h2h_matches) if len(h2h_matches) > 0 else 0.5,
        'h2h_avg_goals': avg_goals_h2h if len(h2h_matches) > 0 else 2.5,
        'h2h_n': len(h2h_matches)
    })

# Pour optimiser, on va utiliser une approche simplifiée pour H2H
df['h2h_home_wins'] = 0.5
df['h2h_avg_goals'] = df['avg_total_goals']
df['h2h_n'] = 0

# Sélectionner les features finales
feature_columns = [
    'home_win_rate', 'home_draw_rate', 'home_avg_goals_scored', 'home_avg_goals_conceded',
    'away_win_rate', 'away_draw_rate', 'away_avg_goals_scored', 'away_avg_goals_conceded',
    'avg_total_goals', 'goal_diff_avg', 'win_rate_diff', 'league_encoded',
    'year', 'month', 'day_of_week', 'h2h_home_wins', 'h2h_avg_goals', 'h2h_n',
    'score_home', 'score_away', 'league'
]

df_features = df[feature_columns].copy()

# Sauvegarder les features
output_file = 'training_features_fifa.csv'
df_features.to_csv(output_file, index=False)
print(f"\nFeatures sauvegardées: {output_file}")
print(f"Nombre de features: {len(df_features)}")
print(f"Nombre de colonnes: {len(df_features.columns)}")

print("\n=== CRÉATION DES FEATURES TERMINÉE ===")
