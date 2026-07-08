"""
Entraînement du modèle Over/Under
=================================
Script pour entraîner le modèle de prédiction Over/Under

Author: SOLITAIRE HACK
Version: 2.0
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=== ENTRAÎNEMENT DU MODÈLE OVER/UNDER ===\n")

# Charger les features
print("Chargement des features...")
df = pd.read_csv('training_features.csv')
print(f"Features chargées: {len(df)} lignes, {len(df.columns)} colonnes")

# Créer la target Over/Under (seuil 6.5)
print("\nCréation de la target Over/Under...")
df['total_goals'] = df['score_home'] + df['score_away']
df['overunder_target'] = (df['total_goals'] > 6.5).astype(int)

print(f"Distribution de la target (seuil 6.5):")
print(df['overunder_target'].value_counts())
print(f"  - Under (0): {len(df[df['overunder_target'] == 0])} ({len(df[df['overunder_target'] == 0])/len(df)*100:.1f}%)")
print(f"  - Over (1): {len(df[df['overunder_target'] == 1])} ({len(df[df['overunder_target'] == 1])/len(df)*100:.1f}%)")

# Sélectionner les features (exclure les colonnes non numériques et les targets)
feature_cols = [
    'home_team_win_rate', 'home_team_draw_rate', 'home_team_avg_goals_scored', 'home_team_avg_goals_conceded',
    'away_team_win_rate', 'away_team_draw_rate', 'away_team_avg_goals_scored', 'away_team_avg_goals_conceded',
    'avg_total_goals', 'goal_diff_avg', 'win_rate_diff', 'league_encoded',
    'year', 'month', 'day_of_week'
]

print(f"\nFeatures utilisées ({len(feature_cols)}):")
for col in feature_cols:
    print(f"  - {col}")

# Préparer X et y
X = df[feature_cols]
y = df['overunder_target']

# Diviser en train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nDivision des données:")
print(f"  - Train: {len(X_train)} échantillons")
print(f"  - Test: {len(X_test)} échantillons")

# Entraîner plusieurs modèles
print("\n=== ENTRAÎNEMENT DES MODÈLES ===\n")

# Random Forest
print("1. Random Forest Classifier...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_score = rf_model.score(X_test, y_test)
print(f"   Accuracy: {rf_score:.4f}")

# Gradient Boosting
print("2. Gradient Boosting Classifier...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
gb_model.fit(X_train, y_train)
gb_score = gb_model.score(X_test, y_test)
print(f"   Accuracy: {gb_score:.4f}")

# Choisir le meilleur modèle
best_model = gb_model if gb_score > rf_score else rf_model
best_name = "Gradient Boosting" if gb_score > rf_score else "Random Forest"

print(f"\n=== MEILLEUR MODÈLE: {best_name} ===")
print(f"Accuracy: {max(rf_score, gb_score):.4f}")

# Évaluation détaillée
y_pred = best_model.predict(X_test)
print("\n=== RAPPORT DE CLASSIFICATION ===")
print(classification_report(y_test, y_pred, target_names=['under', 'over']))

print("\n=== MATRICE DE CONFUSION ===")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Cross-validation
print("\n=== CROSS-VALIDATION ===")
cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='accuracy')
print(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

# Sauvegarder le meilleur modèle
print(f"\nSauvegarde du modèle...")
joblib.dump(best_model, 'overunder_model.pkl')
joblib.dump(feature_cols, 'overunder_feature_columns.pkl')
print("Modèle sauvegardé: overunder_model.pkl")
print("Features sauvegardées: overunder_feature_columns.pkl")

print("\n=== ENTRAÎNEMENT TERMINÉ ===")
print(f"Modèle: {best_name}")
print(f"Accuracy: {max(rf_score, gb_score):.4f}")
print(f"Features: {len(feature_cols)}")
