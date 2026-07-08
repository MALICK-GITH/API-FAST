"""
Entraînement des Modèles par Ligues
===================================
Script pour entraîner les modèles de prédiction par ligue:
- Victoires (match result)
- Total buts
- Parité (pair/impair)

Author: SOLITAIRE HACK
Version: 1.0
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, mean_squared_error, r2_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=== ENTRAÎNEMENT DES MODÈLES PAR LIGUE ===\n")

# Charger les features
print("Chargement des features...")
df = pd.read_csv('training_features_fifa.csv')
print(f"Features chargées: {len(df)} lignes, {len(df.columns)} colonnes")

# Obtenir les ligues
leagues = df['league'].unique()
print(f"\nLigues disponibles: {len(leagues)}")
for i, league in enumerate(sorted(leagues), 1):
    count = len(df[df['league'] == league])
    print(f"  {i:2d}. {league}: {count:,} matchs")

# Créer le répertoire pour les modèles
os.makedirs('models_by_league', exist_ok=True)

# Features pour l'entraînement
feature_cols = [
    'home_win_rate', 'home_draw_rate', 'home_avg_goals_scored', 'home_avg_goals_conceded',
    'away_win_rate', 'away_draw_rate', 'away_avg_goals_scored', 'away_avg_goals_conceded',
    'avg_total_goals', 'goal_diff_avg', 'win_rate_diff', 'league_encoded',
    'year', 'month', 'day_of_week', 'h2h_home_wins', 'h2h_avg_goals', 'h2h_n'
]

print(f"\nFeatures utilisées ({len(feature_cols)}):")

# Entraîner pour chaque ligue
results = []

for league in sorted(leagues):
    print(f"\n{'='*80}")
    print(f"LIGUE: {league}")
    print(f"{'='*80}")
    
    # Filtrer les données pour cette ligue
    df_league = df[df['league'] == league].copy()
    
    if len(df_league) < 100:
        print(f"SKIP: Pas assez de données ({len(df_league)} matchs)")
        continue
    
    print(f"Données: {len(df_league)} matchs")
    
    # Préparer les targets
    df_league['target_result'] = df_league.apply(lambda x: 0 if x['score_home'] < x['score_away'] 
                                                  else 1 if x['score_home'] == x['score_away'] 
                                                  else 2, axis=1)
    df_league['total_goals'] = df_league['score_home'] + df_league['score_away']
    df_league['target_parity'] = (df_league['total_goals'] % 2).astype(int)  # 0 = pair, 1 = impair
    
    # Préparer X
    X = df_league[feature_cols]
    
    # ─── MODÈLE 1: VICTOIRES (Classification) ───
    print("\n1. Entraînement du modèle de victoires...")
    y_result = df_league['target_result']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_result, test_size=0.2, random_state=42, stratify=y_result)
    
    rf_result = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_result.fit(X_train, y_train)
    result_accuracy = rf_result.score(X_test, y_test)
    print(f"   Accuracy: {result_accuracy:.4f}")
    
    # Sauvegarder le modèle
    league_safe_name = league.replace(' ', '_').replace('.', '_').replace('/', '_')
    joblib.dump(rf_result, f'models_by_league/{league_safe_name}_result.pkl')
    joblib.dump(feature_cols, f'models_by_league/{league_safe_name}_result_features.pkl')
    
    # ─── MODÈLE 2: TOTAL BUTS (Régression) ───
    print("\n2. Entraînement du modèle de total buts...")
    y_goals = df_league['total_goals']
    
    X_train_g, X_test_g, y_train_g, y_test_g = train_test_split(X, y_goals, test_size=0.2, random_state=42)
    
    gb_goals = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    gb_goals.fit(X_train_g, y_train_g)
    goals_mse = mean_squared_error(y_test_g, gb_goals.predict(X_test_g))
    goals_r2 = r2_score(y_test_g, gb_goals.predict(X_test_g))
    print(f"   MSE: {goals_mse:.4f}")
    print(f"   R²: {goals_r2:.4f}")
    
    # Sauvegarder le modèle
    joblib.dump(gb_goals, f'models_by_league/{league_safe_name}_goals.pkl')
    joblib.dump(feature_cols, f'models_by_league/{league_safe_name}_goals_features.pkl')
    
    # ─── MODÈLE 3: PARITÉ (Classification) ───
    print("\n3. Entraînement du modèle de parité...")
    y_parity = df_league['target_parity']
    
    X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(X, y_parity, test_size=0.2, random_state=42, stratify=y_parity)
    
    rf_parity = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_parity.fit(X_train_p, y_train_p)
    parity_accuracy = rf_parity.score(X_test_p, y_test_p)
    print(f"   Accuracy: {parity_accuracy:.4f}")
    
    # Sauvegarder le modèle
    joblib.dump(rf_parity, f'models_by_league/{league_safe_name}_parity.pkl')
    joblib.dump(feature_cols, f'models_by_league/{league_safe_name}_parity_features.pkl')
    
    # Enregistrer les résultats
    results.append({
        'league': league,
        'matches': len(df_league),
        'result_accuracy': result_accuracy,
        'goals_mse': goals_mse,
        'goals_r2': goals_r2,
        'parity_accuracy': parity_accuracy
    })

# Résumé des résultats
print(f"\n{'='*80}")
print("RÉSUMÉ DES RÉSULTATS")
print(f"{'='*80}")

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Sauvegarder le résumé
results_df.to_csv('models_summary.csv', index=False)
print(f"\nRésumé sauvegardé: models_summary.csv")

print(f"\n{'='*80}")
print("ENTRAÎNEMENT TERMINÉ")
print(f"{'='*80}")
print(f"Modèles sauvegardés dans: models_by_league/")
print(f"Nombre de ligues entraînées: {len(results)}")
