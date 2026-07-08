import pandas as pd
import numpy as np
from datetime import datetime
import json

# Charger la database historique
print("Chargement de la database historique...")
df = pd.read_csv('finished_matches_clean.csv')

print(f"Nombre de matchs: {len(df)}")
print(f"Colonnes: {df.columns.tolist()}")

# Convertir la date (format ISO8601)
df['finished_at'] = pd.to_datetime(df['finished_at'], format='ISO8601')
df['date'] = df['finished_at'].dt.date
df['year'] = df['finished_at'].dt.year
df['month'] = df['finished_at'].dt.month
df['day_of_week'] = df['finished_at'].dt.dayofweek

# Créer la variable cible (résultat du match)
def get_result(row):
    if row['score_home'] > row['score_away']:
        return 'home_win'  # Victoire domicile
    elif row['score_home'] < row['score_away']:
        return 'away_win'  # Victoire extérieur
    else:
        return 'draw'  # Match nul

df['result'] = df.apply(get_result, axis=1)
df['result_numeric'] = df['result'].map({'home_win': 1, 'draw': 0, 'away_win': 2})

# Calculer les statistiques par équipe
print("\nCalcul des statistiques par équipe...")

def calculate_team_stats(df, team_col='team_home', score_col='score_home', opponent_col='team_away', opponent_score_col='score_away'):
    """Calcule les statistiques pour une équipe (domicile ou extérieur)"""
    stats = []
    
    for team in df[team_col].unique():
        team_matches = df[df[team_col] == team]
        
        total_matches = len(team_matches)
        wins = (team_matches[score_col] > team_matches[opponent_score_col]).sum()
        draws = (team_matches[score_col] == team_matches[opponent_score_col]).sum()
        losses = (team_matches[score_col] < team_matches[opponent_score_col]).sum()
        
        goals_scored = team_matches[score_col].sum()
        goals_conceded = team_matches[opponent_score_col].sum()
        
        stats.append({
            'team': team,
            'total_matches': total_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': wins / total_matches if total_matches > 0 else 0,
            'draw_rate': draws / total_matches if total_matches > 0 else 0,
            'loss_rate': losses / total_matches if total_matches > 0 else 0,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'avg_goals_scored': goals_scored / total_matches if total_matches > 0 else 0,
            'avg_goals_conceded': goals_conceded / total_matches if total_matches > 0 else 0,
            'goal_diff': goals_scored - goals_conceded
        })
    
    return pd.DataFrame(stats)

# Statistiques domicile
home_stats = calculate_team_stats(df, 'team_home', 'score_home', 'team_away', 'score_away')
home_stats.columns = [f'home_{col}' if col != 'team' else col for col in home_stats.columns]

# Statistiques extérieur
away_stats = calculate_team_stats(df, 'team_away', 'score_away', 'team_home', 'score_home')
away_stats.columns = [f'away_{col}' if col != 'team' else col for col in away_stats.columns]

# Fusionner les statistiques
team_stats = home_stats.merge(away_stats, on='team', how='outer', suffixes=('', '_away'))

# Calculer les statistiques globales
team_stats['total_matches'] = team_stats['home_total_matches'].fillna(0) + team_stats['away_total_matches'].fillna(0)
team_stats['total_wins'] = team_stats['home_wins'].fillna(0) + team_stats['away_wins'].fillna(0)
team_stats['total_draws'] = team_stats['home_draws'].fillna(0) + team_stats['away_draws'].fillna(0)
team_stats['total_losses'] = team_stats['home_losses'].fillna(0) + team_stats['away_losses'].fillna(0)
team_stats['total_goals_scored'] = team_stats['home_goals_scored'].fillna(0) + team_stats['away_goals_scored'].fillna(0)
team_stats['total_goals_conceded'] = team_stats['home_goals_conceded'].fillna(0) + team_stats['away_goals_conceded'].fillna(0)

team_stats['global_win_rate'] = team_stats['total_wins'] / team_stats['total_matches'] if team_stats['total_matches'].sum() > 0 else 0
team_stats['global_draw_rate'] = team_stats['total_draws'] / team_stats['total_matches'] if team_stats['total_matches'].sum() > 0 else 0
team_stats['global_loss_rate'] = team_stats['total_losses'] / team_stats['total_matches'] if team_stats['total_matches'].sum() > 0 else 0
team_stats['global_avg_goals_scored'] = team_stats['total_goals_scored'] / team_stats['total_matches'] if team_stats['total_matches'].sum() > 0 else 0
team_stats['global_avg_goals_conceded'] = team_stats['total_goals_conceded'] / team_stats['total_matches'] if team_stats['total_matches'].sum() > 0 else 0

print(f"Statistiques calculées pour {len(team_stats)} équipes")

# Statistiques par ligue
print("\nCalcul des statistiques par ligue...")
league_stats = df.groupby('league').agg({
    'match_id': 'count',
    'score_home': ['mean', 'sum'],
    'score_away': ['mean', 'sum']
}).reset_index()
league_stats.columns = ['league', 'total_matches', 'avg_home_goals', 'total_home_goals', 'avg_away_goals', 'total_away_goals']
league_stats['avg_total_goals'] = league_stats['avg_home_goals'] + league_stats['avg_away_goals']

print(f"Statistiques calculées pour {len(league_stats)} ligues")

# Fusionner les statistiques avec les matchs
print("\nFusion des statistiques avec les matchs...")
df_with_stats = df.merge(team_stats[['team', 'global_win_rate', 'global_draw_rate', 'global_avg_goals_scored', 'global_avg_goals_conceded']], 
                          left_on='team_home', right_on='team', how='left')
df_with_stats = df_with_stats.rename(columns={
    'global_win_rate': 'home_team_win_rate',
    'global_draw_rate': 'home_team_draw_rate',
    'global_avg_goals_scored': 'home_team_avg_goals_scored',
    'global_avg_goals_conceded': 'home_team_avg_goals_conceded'
})

df_with_stats = df_with_stats.merge(team_stats[['team', 'global_win_rate', 'global_draw_rate', 'global_avg_goals_scored', 'global_avg_goals_conceded']], 
                          left_on='team_away', right_on='team', how='left')
df_with_stats = df_with_stats.rename(columns={
    'global_win_rate': 'away_team_win_rate',
    'global_draw_rate': 'away_team_draw_rate',
    'global_avg_goals_scored': 'away_team_avg_goals_scored',
    'global_avg_goals_conceded': 'away_team_avg_goals_conceded'
})

df_with_stats = df_with_stats.merge(league_stats[['league', 'avg_total_goals']], on='league', how='left')

# Supprimer les colonnes temporaires
df_with_stats = df_with_stats.drop(columns=['team_x', 'team_y'])

# Créer des features additionnelles
df_with_stats['goal_diff_avg'] = df_with_stats['home_team_avg_goals_scored'] - df_with_stats['away_team_avg_goals_scored']
df_with_stats['win_rate_diff'] = df_with_stats['home_team_win_rate'] - df_with_stats['away_team_win_rate']

# Encoder les ligues (top 20 ligues les plus fréquentes)
top_leagues = df['league'].value_counts().head(20).index.tolist()
df_with_stats['league_encoded'] = df_with_stats['league'].apply(lambda x: 1 if x in top_leagues else 0)

# Sauvegarder les features
print("\nSauvegarde des features...")
df_with_stats.to_csv('training_features.csv', index=False)

print(f"\n=== RÉSUMÉ ===")
print(f"Features créées: {len(df_with_stats.columns)}")
print(f"Colonnes: {df_with_stats.columns.tolist()}")
print(f"\nAperçu des données:")
print(df_with_stats.head())

print(f"\nDistribution des résultats:")
print(df_with_stats['result'].value_counts())

print(f"\nFeatures sauvegardées dans 'training_features.csv'")
