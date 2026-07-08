import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=== ENTRAÎNEMENT DU MODÈLE DE PRÉDICTION FIFA ===\n")

# Charger les features
print("Chargement des features...")
df = pd.read_csv('training_features.csv')

print(f"Nombre de matchs: {len(df)}")
print(f"Features disponibles: {df.columns.tolist()}")

# Sélectionner les features pour l'entraînement
feature_columns = [
    'home_team_win_rate',
    'home_team_draw_rate', 
    'home_team_avg_goals_scored',
    'home_team_avg_goals_conceded',
    'away_team_win_rate',
    'away_team_draw_rate',
    'away_team_avg_goals_scored',
    'away_team_avg_goals_conceded',
    'avg_total_goals',
    'goal_diff_avg',
    'win_rate_diff',
    'league_encoded',
    'year',
    'month',
    'day_of_week'
]

# Supprimer les lignes avec des valeurs manquantes
df_model = df[feature_columns + ['result_numeric']].dropna()

print(f"Matchs après nettoyage: {len(df_model)}")

# Séparer X et y
X = df_model[feature_columns]
y = df_model['result_numeric']

print(f"\nDistribution des classes:")
print(y.value_counts())

# Diviser en train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTaille train: {len(X_train)}")
print(f"Taille test: {len(X_test)}")

# Essayer plusieurs modèles
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
rf_train_score = rf_model.score(X_train, y_train)
rf_test_score = rf_model.score(X_test, y_test)

print(f"   Score train: {rf_train_score:.4f}")
print(f"   Score test: {rf_test_score:.4f}")

# Cross-validation
rf_cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)
print(f"   Cross-validation score: {rf_cv_scores.mean():.4f} (+/- {rf_cv_scores.std() * 2:.4f})")

# Gradient Boosting
print("\n2. Gradient Boosting Classifier...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

gb_model.fit(X_train, y_train)
gb_train_score = gb_model.score(X_train, y_train)
gb_test_score = gb_model.score(X_test, y_test)

print(f"   Score train: {gb_train_score:.4f}")
print(f"   Score test: {gb_test_score:.4f}")

# Cross-validation
gb_cv_scores = cross_val_score(gb_model, X_train, y_train, cv=5)
print(f"   Cross-validation score: {gb_cv_scores.mean():.4f} (+/- {gb_cv_scores.std() * 2:.4f})")

# Sélectionner le meilleur modèle
if rf_test_score >= gb_test_score:
    best_model = rf_model
    best_model_name = "Random Forest"
    best_score = rf_test_score
else:
    best_model = gb_model
    best_model_name = "Gradient Boosting"
    best_score = gb_test_score

print(f"\n=== MEILLEUR MODÈLE: {best_model_name} ===")
print(f"Score test: {best_score:.4f}")

# Évaluation détaillée du meilleur modèle
y_pred = best_model.predict(X_test)

print("\n=== RAPPORT DE CLASSIFICATION ===")
print(classification_report(y_test, y_pred, target_names=['Away Win', 'Draw', 'Home Win']))

print("\n=== MATRICE DE CONFUSION ===")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Importance des features
print("\n=== IMPORTANCE DES FEATURES ===")
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance)

# Sauvegarder le modèle
print(f"\nSauvegarde du modèle...")
joblib.dump(best_model, 'fifa_prediction_model.pkl')
joblib.dump(feature_columns, 'feature_columns.pkl')

print("Modèle sauvegardé: 'fifa_prediction_model.pkl'")
print("Features sauvegardées: 'feature_columns.pkl'")

# Sauvegarder les statistiques des équipes pour les prédictions futures
team_stats = df[['team_home', 'home_team_win_rate', 'home_team_draw_rate', 
                  'home_team_avg_goals_scored', 'home_team_avg_goals_conceded']].drop_duplicates()
team_stats = team_stats.rename(columns={
    'team_home': 'team',
    'home_team_win_rate': 'win_rate',
    'home_team_draw_rate': 'draw_rate',
    'home_team_avg_goals_scored': 'avg_goals_scored',
    'home_team_avg_goals_conceded': 'avg_goals_conceded'
})

team_stats.to_csv('team_stats.csv', index=False)
print("Statistiques équipes sauvegardées: 'team_stats.csv'")

print("\n=== ENTRAÎNEMENT TERMINÉ ===")
