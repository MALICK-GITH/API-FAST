# INTEGRATION API FIFA PREDICTION

## 📋 Vue d'ensemble

L'API FIFA Prediction fournit des prédictions de matchs FIFA en utilisant des modèles d'apprentissage automatique entraînés sur des données historiques. L'API est conçue pour être intégrée directement avec les plateformes de paris.

## 🔗 Configuration

- **URL de base:** `http://localhost:5000`
- **Port:** 5000
- **Format:** JSON
- **Méthode:** POST pour les prédictions

## 📡 Endpoints Disponibles

### 1. `/health` (GET)
Vérifie la santé de l'API.

**Réponse:**
```json
{
  "status": "healthy",
  "models_loaded": 18,
  "leagues_supported": 18
}
```

### 2. `/leagues` (GET)
Liste toutes les ligues supportées.

**Réponse:**
```json
{
  "total": 18,
  "leagues": [
    {
      "name": "FC 26. 5x5 Rush. Superligue",
      "family": "RUSH",
      "models_available": ["result", "goals", "parity"]
    }
  ]
}
```

### 3. `/predict` (POST)
Prédiction pour un match unique.

**Format d'entrée (format plateforme):**
```json
{
  "I": "734915710",
  "O1": "Barcelone",
  "O2": "Galatasaray",
  "L": "FC 26. 5x5 Rush. Superligue",
  "S": 1783516200,
  "E": [
    {"T": 1, "C": 1.096},
    {"T": 2, "C": 6.14},
    {"T": 3, "C": 30}
  ]
}
```

**Réponse:**
```json
{
  "success": true,
  "I": "734915710",
  "O1": "Barcelone",
  "O2": "Galatasaray",
  "L": "FC 26. 5x5 Rush. Superligue",
  "predictions": {
    "match_result": {
      "prediction": "home_win",
      "confidence": 0.52,
      "probabilities": {
        "home_win": 0.52,
        "draw": 0.35,
        "away_win": 0.13
      }
    },
    "total_goals": {
      "predicted": 7.4,
      "platform_value": 7.5
    },
    "total_parity": {
      "prediction": "even",
      "confidence": 0.55
    },
    "over_under": {
      "threshold": 6.5,
      "prediction": "over",
      "confidence": 0.92
    }
  },
  "platform_odds": {
    "main": {
      "home_win": {"value": 1.096},
      "draw": {"value": 6.14},
      "away_win": {"value": 30}
    }
  },
  "timestamp": 1783516200
}
```

### 4. `/predict/batch` (POST)
Prédictions pour plusieurs matchs.

**Format d'entrée:**
```json
{
  "matches": [
    {
      "I": "734915710",
      "O1": "Barcelone",
      "O2": "Galatasaray",
      "L": "FC 26. 5x5 Rush. Superligue",
      "S": 1783516200
    },
    {
      "I": "734917661",
      "O1": "Fenerbahçe",
      "O2": "Lombardia",
      "L": "FC 26. 5x5 Rush. Superligue",
      "S": 1783516800
    }
  ]
}
```

**Réponse:**
```json
{
  "success": true,
  "total_matches": 2,
  "predictions": [
    {...},
    {...}
  ]
}
```

### 5. `/model/{league_name}` (GET)
Informations sur le modèle d'une ligue spécifique.

**Réponse:**
```json
{
  "league": "FC 26. 5x5 Rush. Superligue",
  "family": "RUSH",
  "models": {
    "match_result": {
      "type": "RandomForestClassifier",
      "accuracy": 0.72
    },
    "total_goals": {
      "type": "GradientBoostingRegressor",
      "accuracy": 0.85
    },
    "total_parity": {
      "type": "RandomForestClassifier",
      "accuracy": 0.68
    }
  }
}
```

## 📝 Format des Données

### Champs d'Entrée (Format Plateforme)

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| I | string | Oui | Identifiant du match |
| O1 | string | Oui | Équipe domicile |
| O2 | string | Oui | Équipe extérieur |
| L | string | Oui | Nom de la ligue |
| S | integer | Non | Timestamp Unix |
| SC | object | Non | Score et statut |
| E | array | Non | Cotes principales |
| AE | array | Non | Cotes additionnelles |

### Codes de Cote (E.T)

| Code | Description |
|------|-------------|
| T=1 | Victoire domicile (Home Win) |
| T=2 | Match nul (Draw) |
| T=3 | Victoire extérieur (Away Win) |
| T=4 | No Bet |
| T=5 | BTTS Non |
| T=6 | BTTS Oui |
| T=7 | Handicap domicile |
| T=8 | Handicap extérieur |
| T=9 | Over (Plus de) |
| T=10 | Under (Moins de) |
| T=11-14 | Over/Under (variantes) |
| T=180-181 | Double Chance |

### Codes de Groupe (AE.G)

| Code | Description |
|------|-------------|
| G=2 | Handicap |
| G=17 | Total Goals |

## 🏆 Ligues Supportées

### Ligues RUSH (5x5)
- FC 26. 5x5 Rush. Superligue

### Ligues CLASSIC (4x4)
- FC 24. 4x4. Championnat d'Angleterre

### Ligues CHAMPIONS
- FC 26. Champions League

### Ligues CLASSIC (3x3)
- FC 25. 3x3. Ligue de conférence

### Ligues WORLD
- FC 26. Championnat du monde

### Ligues CLASSIC (Championnats nationaux)
- FC 25. Italy Championship
- FC 25. Championnat d'Angleterre
- FC 25. Championnat d'Allemagne
- FC 25. Spain Championship

## 🔧 Types de Prédictions

### 1. Match Result (1X2)
- **home_win**: Victoire domicile
- **draw**: Match nul
- **away_win**: Victoire extérieur
- **confidence**: Niveau de confiance (0-1)
- **probabilities**: Probabilités pour chaque résultat

### 2. Total Goals
- **predicted**: Nombre de buts prédit
- **platform_value**: Valeur la plus proche sur la plateforme
- **confidence**: Niveau de confiance

### 3. Total Parity
- **even**: Total pair
- **odd**: Total impair
- **confidence**: Niveau de confiance

### 4. Over/Under
- **threshold**: Seuil de buts (adapté selon la famille)
- **over**: Plus de X buts
- **under**: Moins de X buts
- **confidence**: Niveau de confiance

## 🚀 Démarrage Rapide

### 1. Démarrer l'API

```bash
python prediction_api_league.py
```

### 2. Tester avec cURL

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "I": "734915710",
    "O1": "Barcelone",
    "O2": "Galatasaray",
    "L": "FC 26. 5x5 Rush. Superligue",
    "S": 1783516200
  }'
```

### 3. Tester avec Python

```python
import requests

response = requests.post(
    'http://localhost:5000/predict',
    json={
        'I': '734915710',
        'O1': 'Barcelone',
        'O2': 'Galatasaray',
        'L': 'FC 26. 5x5 Rush. Superligue',
        'S': 1783516200
    }
)

print(response.json())
```

## 📊 Traitement des Données Live

Pour traiter les données live de la plateforme:

1. Sauvegardez le JSON dans `live_data_input.json`
2. Exécutez:
   ```bash
   python process_full_live_data.py
   ```
3. Le rapport sera sauvegardé dans `live_predictions_report.json`

## ⚠️ Codes d'Erreur

| Code | Message | Description |
|------|---------|-------------|
| 400 | BAD_REQUEST | Format de requête invalide |
| 404 | LEAGUE_NOT_FOUND | Ligue non trouvée ou non supportée |
| 500 | INTERNAL_ERROR | Erreur interne du serveur |
| 503 | MODEL_NOT_LOADED | Modèle non chargé pour cette ligue |

## 📚 Documentation Complète

Pour plus de détails sur les formats et les codes, exécutez:

```bash
python integration_spec_platform.py
```

---

**Author:** SOLITAIRE HACK  
**Version:** 2.0  
**Date:** 2026-07-08
