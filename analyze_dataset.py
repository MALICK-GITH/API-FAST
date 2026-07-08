"""
Analyse du Dataset FIFA
=======================
Script pour analyser le dataset de matchs terminés

Author: SOLITAIRE HACK
Version: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_dataset(csv_path: str = 'finished_matches_clean.csv'):
    """
    Analyse le dataset de matchs terminés
    
    Args:
        csv_path: Chemin vers le fichier CSV du dataset
    """
    print("=== ANALYSE DU DATASET FIFA ===\n")
    
    # Charger le dataset
    df = pd.read_csv(csv_path)
    
    print(f"📊 INFORMATIONS GÉNÉRALES")
    print(f"Nombre total de matchs: {len(df):,}")
    print(f"Colonnes disponibles: {len(df.columns)}")
    print(f"\nColonnes:")
    for col in df.columns:
        print(f"  - {col}")
    
    print(f"\n🏆 LIGUES PRÉSENTES")
    leagues = df['league'].unique()
    print(f"Nombre de ligues: {len(leagues)}")
    
    for league in sorted(leagues):
        count = len(df[df['league'] == league])
        percentage = (count / len(df)) * 100
        print(f"  - {league}: {count:,} matchs ({percentage:.1f}%)")
    
    print(f"\n⚽ DISTRIBUTION DES SCORES")
    print("Score domicile:")
    print(df['score_home'].describe())
    print("\nScore extérieur:")
    print(df['score_away'].describe())
    
    print(f"\n📈 STATISTIQUES PAR LIGUE")
    league_stats = []
    for league in sorted(leagues):
        league_df = df[df['league'] == league]
        avg_home = league_df['score_home'].mean()
        avg_away = league_df['score_away'].mean()
        avg_total = (league_df['score_home'] + league_df['score_away']).mean()
        median_total = (league_df['score_home'] + league_df['score_away']).median()
        
        league_stats.append({
            'league': league,
            'matches': len(league_df),
            'avg_home': avg_home,
            'avg_away': avg_away,
            'avg_total': avg_total,
            'median_total': median_total
        })
    
    # Trier par moyenne totale
    league_stats.sort(key=lambda x: x['avg_total'], reverse=True)
    
    print(f"{'Ligue':<50} {'Matchs':>8} {'Avg Home':>10} {'Avg Away':>10} {'Avg Total':>10} {'Median':>10}")
    print("-" * 100)
    for stat in league_stats:
        print(f"{stat['league']:<50} {stat['matches']:>8,} {stat['avg_home']:>10.2f} {stat['avg_away']:>10.2f} {stat['avg_total']:>10.2f} {stat['median_total']:>10.2f}")
    
    print(f"\n🎯 DISTRIBUTION DES RÉSULTATS")
    df['result'] = df.apply(lambda x: 'home_win' if x['score_home'] > x['score_away'] 
                           else 'away_win' if x['score_home'] < x['score_away'] 
                           else 'draw', axis=1)
    
    result_counts = df['result'].value_counts()
    print(f"Victoires domicile: {result_counts.get('home_win', 0):,} ({result_counts.get('home_win', 0)/len(df)*100:.1f}%)")
    print(f"Victoires extérieur: {result_counts.get('away_win', 0):,} ({result_counts.get('away_win', 0)/len(df)*100:.1f}%)")
    print(f"Matchs nuls: {result_counts.get('draw', 0):,} ({result_counts.get('draw', 0)/len(df)*100:.1f}%)")
    
    print(f"\n🔥 SCORES EXACTS LES PLUS FRÉQUENTS")
    df['score'] = df['score_home'].astype(str) + '-' + df['score_away'].astype(str)
    score_counts = df['score'].value_counts().head(20)
    for score, count in score_counts.items():
        print(f"  {score}: {count:,} matchs ({count/len(df)*100:.2f}%)")
    
    print(f"\n📊 ANALYSE DES BUTS TOTAUX")
    df['total_goals'] = df['score_home'] + df['score_away']
    print(f"Moyenne buts par match: {df['total_goals'].mean():.2f}")
    print(f"Médiane buts par match: {df['total_goals'].median():.2f}")
    print(f"Min buts: {df['total_goals'].min()}")
    print(f"Max buts: {df['total_goals'].max()}")
    
    print(f"\nDistribution des buts totaux:")
    for goals in sorted(df['total_goals'].unique()):
        count = len(df[df['total_goals'] == goals])
        print(f"  {goals} buts: {count:,} matchs ({count/len(df)*100:.1f}%)")
    
    print(f"\n🎲 BTTS (Both Teams To Score)")
    df['btts'] = df.apply(lambda x: 'yes' if x['score_home'] > 0 and x['score_away'] > 0 else 'no', axis=1)
    btts_counts = df['btts'].value_counts()
    print(f"BTTS Yes: {btts_counts.get('yes', 0):,} ({btts_counts.get('yes', 0)/len(df)*100:.1f}%)")
    print(f"BTTS No: {btts_counts.get('no', 0):,} ({btts_counts.get('no', 0)/len(df)*100:.1f}%)")
    
    print(f"\n🏅 ÉQUIPES LES PLUS PRÉSENTES")
    team_home_counts = df['team_home'].value_counts().head(10)
    team_away_counts = df['team_away'].value_counts().head(10)
    
    print("Équipes domicile (top 10):")
    for team, count in team_home_counts.items():
        print(f"  - {team}: {count:,} matchs")
    
    print("\nÉquipes extérieur (top 10):")
    for team, count in team_away_counts.items():
        print(f"  - {team}: {count:,} matchs")
    
    print(f"\n✅ ANALYSE TERMINÉE")
    print(f"Dataset analysé: {csv_path}")
    print(f"Date de l'analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    analyze_dataset()
