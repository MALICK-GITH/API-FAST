import pandas as pd
import numpy as np

# Charger le fichier CSV
df = pd.read_csv('finished_matches.csv')

print(f"Nombre total de matchs: {len(df)}")
print(f"\nColonnes: {df.columns.tolist()}")

# Vérifier les valeurs uniques de la colonne 'finished_at'
print(f"\nValeurs manquantes dans 'finished_at': {df['finished_at'].isna().sum()}")

# Filtrer uniquement les matchs terminés (ceux qui ont une date finished_at)
df_clean = df[df['finished_at'].notna()].copy()

print(f"\nNombre de matchs terminés: {len(df_clean)}")

# Supprimer les colonnes métadonnées inutiles si nécessaire
columns_to_keep = ['match_id', 'team_home', 'team_away', 'league', 'score_home', 'score_away', 'finished_at']
df_clean = df_clean[columns_to_keep]

# Sauvegarder le fichier nettoyé
df_clean.to_csv('finished_matches_clean.csv', index=False)

print(f"\nFichier nettoyé sauvegardé: finished_matches_clean.csv")
print(f"Matchs conservés: {len(df_clean)}")
