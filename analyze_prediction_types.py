import pandas as pd
import numpy as np
from datetime import datetime

print("=== ANALYSE DES TYPES DE PRÉDICTIONS POSSIBLES ===\n")

# Charger la base de données
df = pd.read_csv('finished_matches_clean.csv')

# Convertir la date
df['finished_at'] = pd.to_datetime(df['finished_at'], format='ISO8601')

print(f"Base de données: {len(df)} matchs")
print(f"Période: {df['finished_at'].min()} à {df['finished_at'].max()}")
print(f"Équipes uniques: {len(df['team_home'].unique()) + len(df['team_away'].unique())}")
print(f"Ligues uniques: {len(df['league'].unique())}")
print()

# === 1. PRÉDICTION DU RÉSULTAT DU MATCH (déjà implémenté) ===
print("=== 1. PRÉDICTION DU RÉSULTAT DU MATCH ===")
print("Type: Classification (3 classes)")
print("Classes: home_win, draw, away_win")

df['result'] = df.apply(lambda row: 'home_win' if row['score_home'] > row['score_away'] 
                        else ('away_win' if row['score_home'] < row['score_away'] else 'draw'), axis=1)

print(f"Distribution: {df['result'].value_counts().to_dict()}")
print(f"Features possibles: statistiques équipes, forme récente, historique tête-à-tête")
print()

# === 2. PRÉDICTION DU SCORE EXACT ===
print("=== 2. PRÉDICTION DU SCORE EXACT ===")
print("Type: Classification multi-classes ou régression")
print("Output: score_home et score_away")

df['score_exact'] = df['score_home'].astype(str) + '-' + df['score_away'].astype(str)
top_scores = df['score_exact'].value_counts().head(10)
print(f"Top 10 scores les plus fréquents:")
for score, count in top_scores.items():
    print(f"  {score}: {count} matchs ({count/len(df)*100:.1f}%)")
print(f"Features possibles: attaque/défense équipes, moyenne buts, forme offensive")
print()

# === 3. PRÉDICTION DU NOMBRE DE BUTS TOTAL (OVER/UNDER) ===
print("=== 3. PRÉDICTION DU NOMBRE DE BUTS TOTAL ===")
print("Type: Classification (over/under) ou régression")
print("Seuils possibles: 2.5, 3.5, 4.5 buts")

df['total_goals'] = df['score_home'] + df['score_away']
print(f"Moyenne buts par match: {df['total_goals'].mean():.2f}")
print(f"Médiane: {df['total_goals'].median():.2f}")
print(f"Max: {df['total_goals'].max()}, Min: {df['total_goals'].min()}")

for threshold in [2.5, 3.5, 4.5]:
    over = (df['total_goals'] > threshold).sum()
    under = (df['total_goals'] <= threshold).sum()
    print(f"  Over/Under {threshold}: Over {over} ({over/len(df)*100:.1f}%), Under {under} ({under/len(df)*100:.1f}%)")
print(f"Features possibles: moyenne buts ligue, style de jeu, importance du match")
print()

# === 4. PRÉDICTION DES BUTS PAR ÉQUIPE ===
print("=== 4. PRÉDICTION DES BUTS PAR ÉQUIPE ===")
print("Type: Classification ou régression")
print("Output: buts domicile et buts extérieur")

print(f"Moyenne buts domicile: {df['score_home'].mean():.2f}")
print(f"Moyenne buts extérieur: {df['score_away'].mean():.2f}")
print(f"Équipes qui marquent > 2 buts à domicile: {(df['score_home'] > 2).sum()} ({(df['score_home'] > 2).sum()/len(df)*100:.1f}%)")
print(f"Équipes qui encaissent > 2 buts à domicile: {(df['score_away'] > 2).sum()} ({(df['score_away'] > 2).sum()/len(df)*100:.1f}%)")
print(f"Features possibles: force attaque/défense, forme offensive/défensive")
print()

# === 5. PRÉDICTION DE LA DIFFÉRENCE DE BUTS ===
print("=== 5. PRÉDICTION DE LA DIFFÉRENCE DE BUTS ===")
print("Type: Classification ou régression")
print("Classes: victoire large, victoire étroite, match nul, défaite étroite, défaite large")

df['goal_diff'] = df['score_home'] - df['score_away']
print(f"Moyenne différence: {df['goal_diff'].mean():.2f}")
print(f"Écart-type: {df['goal_diff'].std():.2f}")

# Catégoriser la différence
def categorize_diff(diff):
    if diff >= 3:
        return 'large_home_win'
    elif diff >= 1:
        return 'narrow_home_win'
    elif diff == 0:
        return 'draw'
    elif diff <= -3:
        return 'large_away_win'
    else:
        return 'narrow_away_win'

df['diff_category'] = df['goal_diff'].apply(categorize_diff)
print(f"Distribution des catégories:")
for cat, count in df['diff_category'].value_counts().items():
    print(f"  {cat}: {count} ({count/len(df)*100:.1f}%)")
print(f"Features possibles: écart de niveau, motivation, historique")
print()

# === 6. PRÉDICTION BTTS (BOTH TEAMS TO SCORE) ===
print("=== 6. PRÉDICTION BTTS (LES DEUX ÉQUIPES MARQUENT) ===")
print("Type: Classification binaire")
print("Classes: Oui, Non")

df['btts'] = (df['score_home'] > 0) & (df['score_away'] > 0)
btts_yes = df['btts'].sum()
btts_no = (~df['btts']).sum()
print(f"BTTS Oui: {btts_yes} ({btts_yes/len(df)*100:.1f}%)")
print(f"BTTS Non: {btts_no} ({btts_no/len(df)*100:.1f}%)")
print(f"Features possibles: force attaque des deux équipes, faiblesse défensive")
print()

# === 7. PRÉDICTION DU VAINQUEUR À LA MI-TEMPS ===
print("=== 7. PRÉDICTION DU VAINQUEUR À LA MI-TEMPS ===")
print("Type: Classification (nécessite données de mi-temps)")
print("Classes: home_win_ht, draw_ht, away_win_ht")
print("⚠️ Nécessite des données de score à la mi-temps (non disponibles dans la base actuelle)")
print(f"Features possibles: forme en début de match, stratégie de début de match")
print()

# === 8. PRÉDICTION DU PREMIER BUTEUR ===
print("=== 8. PRÉDICTION DU PREMIER BUTEUR ===")
print("Type: Classification multi-classes")
print("Classes: équipe domicile, équipe extérieur, pas de but")
print("⚠️ Nécessite des données temporelles sur les buts (non disponibles)")
print(f"Features possibles: statistiques de premier but, agressivité en début de match")
print()

# === 9. PRÉDICTION DE LA LIGUE/COMPÉTITION ===
print("=== 9. PRÉDICTION DU RÉSULTAT PAR LIGUE ===")
print("Type: Classification spécifique par ligue")
print("Approche: Entraîner un modèle par ligue pour plus de précision")

print(f"Top 10 ligues par nombre de matchs:")
for league, count in df['league'].value_counts().head(10).items():
    print(f"  {league}: {count} matchs")
print(f"Features possibles: caractéristiques spécifiques à chaque ligue")
print()

# === 10. PRÉDICTION DE SÉRIE (FORME) ===
print("=== 10. PRÉDICTION DE SÉRIE (FORME) ===")
print("Type: Classification basée sur la forme récente")
print("Output: probabilité de victoire basée sur les N derniers matchs")

print(f"⚠️ Nécessite un ordre chronologique des matchs par équipe")
print(f"Features possibles: forme sur 5/10 derniers matchs, tendance")
print()

# === RÉCAPITULATIF DES MODÈLES POSSIBLES ===
print("\n" + "="*60)
print("=== RÉCAPITULATIF DES MODÈLES DE PRÉDICTION POSSIBLES ===")
print("="*60)

models_summary = [
    {
        "nom": "Résultat du match",
        "type": "Classification (3 classes)",
        "difficulté": "Facile",
        "données": "Disponibles",
        "précision_estimée": "53-55%"
    },
    {
        "nom": "Score exact",
        "type": "Classification multi-classes",
        "difficulté": "Très difficile",
        "données": "Disponibles",
        "précision_estimée": "10-15%"
    },
    {
        "nom": "Over/Under buts",
        "type": "Classification binaire",
        "difficulté": "Moyen",
        "données": "Disponibles",
        "précision_estimée": "55-60%"
    },
    {
        "nom": "Buts par équipe",
        "type": "Régression",
        "difficulté": "Moyen",
        "données": "Disponibles",
        "précision_estimée": "RMSE 1.2-1.5"
    },
    {
        "nom": "Différence de buts",
        "type": "Classification (5 classes)",
        "difficulté": "Moyen",
        "données": "Disponibles",
        "précision_estimée": "45-50%"
    },
    {
        "nom": "BTTS (Both Teams Score)",
        "type": "Classification binaire",
        "difficulté": "Facile",
        "données": "Disponibles",
        "précision_estimée": "55-60%"
    },
    {
        "nom": "Vainqueur mi-temps",
        "type": "Classification (3 classes)",
        "difficulté": "Moyen",
        "données": "Non disponibles",
        "précision_estimée": "N/A"
    },
    {
        "nom": "Premier buteur",
        "type": "Classification multi-classes",
        "difficulté": "Très difficile",
        "données": "Non disponibles",
        "précision_estimée": "N/A"
    },
    {
        "nom": "Modèle par ligue",
        "type": "Classification spécifique",
        "difficulté": "Moyen",
        "données": "Disponibles",
        "précision_estimée": "55-65%"
    },
    {
        "nom": "Forme récente",
        "type": "Classification temporelle",
        "difficulté": "Difficile",
        "données": "Partiellement disponibles",
        "précision_estimée": "50-55%"
    }
]

print(f"{'Modèle':<25} {'Type':<30} {'Difficulté':<15} {'Données':<15} {'Précision':<15}")
print("-" * 100)
for model in models_summary:
    print(f"{model['nom']:<25} {model['type']:<30} {model['difficulté']:<15} {model['données']:<15} {model['précision_estimée']:<15}")

print("\n" + "="*60)
print("=== RECOMMANDATIONS ===")
print("="*60)
print("1. Priorité haute: Résultat du match (déjà implémenté)")
print("2. Priorité haute: Over/Under buts (demande fréquente)")
print("3. Priorité haute: BTTS (demande fréquente)")
print("4. Priorité moyenne: Buts par équipe")
print("5. Priorité moyenne: Différence de buts")
print("6. Priorité basse: Score exact (trop difficile)")
print("7. Priorité basse: Modèles spécifiques par ligue (si beaucoup de données)")
print()
print("Pour améliorer la précision:")
print("- Ajouter plus de features (forme récente, blessures, météo)")
print("- Utiliser des modèles d'ensemble (stacking, blending)")
print("- Collecter plus de données historiques")
print("- Entraîner des modèles spécifiques par ligue pour les grandes ligues")

print("\n=== ANALYSE TERMINÉE ===")
