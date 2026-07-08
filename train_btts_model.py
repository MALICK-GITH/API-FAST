import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

print("=== ENTRAÎNEMENT DU MODÈLE BTTS (Both Teams Score) ===\n")

# Charger les features d'entraînement existants
df = pd.read_csv('training_features.csv')

# Créer la target pour BTTS
# BTTS = 1 si les deux équipes marquent (score_home > 0 ET score_away > 0)
df['btts_target'] = ((df['score_home'] > 0) & (df['score_away'] > 0)).astype(int)

print(f"Distribution BTTS:")
print(f"BTTS Oui (les deux marquent): {df['btts_target'].sum()} ({df['btts_target'].sum()/len(df)*100:.1f}%)")
print(f"BTTS Non (une équipe ne marque pas): {(df['btts_target']==0).sum()} ({(df['btts_target']==0).sum()/len(df)*100:.1f}%)")
print()

# Séparer features et target - utiliser uniquement les colonnes numériques
exclude_cols = ['match_id', 'team_home', 'team_away', 'league', 'score_home', 'score_away', 'finished_at', 'date', 'result', 'result_numeric', 'overunder_target', 'btts_target']
feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['int64', 'float64']]
X = df[feature_cols]
y = df['btts_target']

print(f"Features utilisées: {len(feature_cols)}")
print(f"Features: {feature_cols}")
print()

# Diviser en train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Train set: {len(X_train)} matchs")
print(f"Test set: {len(X_test)} matchs")
print()

# Entraîner plusieurs modèles
print("=== ENTRAÎNEMENT DES MODÈLES ===\n")

models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
}

results = {}

for name, model in models.items():
    print(f"Entraînement de {name}...")
    model.fit(X_train, y_train)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"  Cross-validation accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    # Test accuracy
    test_score = model.score(X_test, y_test)
    print(f"  Test accuracy: {test_score:.4f}")
    
    results[name] = {
        'model': model,
        'cv_score': cv_scores.mean(),
        'test_score': test_score
    }
    print()

# Sélectionner le meilleur modèle
best_model_name = max(results.keys(), key=lambda k: results[k]['test_score'])
best_model = results[best_model_name]['model']

print(f"=== MEILLEUR MODÈLE: {best_model_name} ===")
print(f"Test accuracy: {results[best_model_name]['test_score']:.4f}")
print()

# Rapport de classification détaillé
y_pred = best_model.predict(X_test)
print("=== RAPPORT DE CLASSIFICATION ===")
print(classification_report(y_test, y_pred, target_names=['Non', 'Oui']))
print()

# Matrice de confusion
print("=== MATRICE DE CONFUSION ===")
cm = confusion_matrix(y_test, y_pred)
print(f"              Prédit Non    Prédit Oui")
print(f"Réel Non      {cm[0][0]:<15} {cm[0][1]:<15}")
print(f"Réel Oui      {cm[1][0]:<15} {cm[1][1]:<15}")
print()

# Importance des features
print("=== IMPORTANCE DES FEATURES ===")
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance.head(15))
print()

# Sauvegarder le modèle
joblib.dump(best_model, 'btts_model.pkl')
joblib.dump(feature_cols, 'btts_feature_columns.pkl')

print("=== MODÈLE SAUVEGARDÉ ===")
print("Fichiers créés:")
print("  - btts_model.pkl")
print("  - btts_feature_columns.pkl")
print()

print("=== ENTRAÎNEMENT TERMINÉ ===")
