"""
Filtrage des matchs FIFA
========================
Script pour filtrer uniquement les matchs de ligues FIFA et supprimer les autres

Author: SOLITAIRE HACK
Version: 1.0
"""

import pandas as pd
import numpy as np

print("=== FILTRAGE DES MATCHS FIFA ===\n")

# Charger le dataset
input_file = r'c:\Users\HP\Downloads\finished_matches (2).csv'
print(f"Chargement du dataset: {input_file}")
df = pd.read_csv(input_file)
print(f"Dataset chargé: {len(df):,} matchs")

# Analyser les ligues
print(f"\n=== ANALYSE DES LIGUES ===")
leagues = df['league'].unique()
print(f"Nombre total de ligues: {len(leagues)}")

print("\nToutes les ligues:")
for i, league in enumerate(sorted(leagues), 1):
    count = len(df[df['league'] == league])
    print(f"{i:3d}. {league}: {count:,} matchs")

# Identifier les ligues FIFA (commencent par "FC" ou contiennent "FIFA")
fifa_keywords = ['FC', 'FIFA']
fifa_leagues = [league for league in leagues if any(keyword in league for keyword in fifa_keywords)]
non_fifa_leagues = [league for league in leagues if not any(keyword in league for keyword in fifa_keywords)]

print(f"\n=== LIGUES FIFA ({len(fifa_leagues)}) ===")
for i, league in enumerate(sorted(fifa_leagues), 1):
    count = len(df[df['league'] == league])
    print(f"{i:3d}. {league}: {count:,} matchs")

print(f"\n=== LIGUES NON FIFA ({len(non_fifa_leagues)}) ===")
for i, league in enumerate(sorted(non_fifa_leagues), 1):
    count = len(df[df['league'] == league])
    print(f"{i:3d}. {league}: {count:,} matchs")

# Filtrer uniquement les matchs FIFA
print(f"\n=== FILTRAGE ===")
df_fifa = df[df['league'].isin(fifa_leagues)].copy()
df_non_fifa = df[df['league'].isin(non_fifa_leagues)].copy()

print(f"Matchs FIFA conservés: {len(df_fifa):,} ({len(df_fifa)/len(df)*100:.1f}%)")
print(f"Matchs non FIFA supprimés: {len(df_non_fifa):,} ({len(df_non_fifa)/len(df)*100:.1f}%)")

# Sauvegarder le dataset filtré
output_file = 'finished_matches_fifa.csv'
df_fifa.to_csv(output_file, index=False)
print(f"\nDataset FIFA sauvegardé: {output_file}")

# Sauvegarder aussi les matchs non FIFA pour référence
output_non_fifa = 'finished_matches_non_fifa.csv'
df_non_fifa.to_csv(output_non_fifa, index=False)
print(f"Dataset non FIFA sauvegardé: {output_non_fifa}")

print("\n=== FILTRAGE TERMINÉ ===")
