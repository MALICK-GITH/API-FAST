"""
Spécification d'Intégration API FIFA Prediction
================================================
Document définissant les formats d'entrée et de sortie pour l'intégration
avec les plateformes de paris

Author: SOLITAIRE HACK
Version: 1.0
"""

import json

# ─────────────────────────────────────────
# FORMAT D'ENTRÉE (Données envoyées par les plateformes)
# ─────────────────────────────────────────

INPUT_FORMAT = {
    "description": "Format JSON pour les requêtes de prédiction (format plateforme)",
    "endpoint": "/predict",
    "method": "POST",
    "content_type": "application/json",
    "structure": {
        "I": {
            "type": "string",
            "required": True,
            "description": "Identifiant unique du match"
        },
        "O1": {
            "type": "string",
            "required": True,
            "description": "Nom de l'équipe domicile"
        },
        "O2": {
            "type": "string",
            "required": True,
            "description": "Nom de l'équipe extérieur"
        },
        "L": {
            "type": "string",
            "required": true,
            "description": "Nom de la ligue/compétition"
        },
        "S": {
            "type": "integer",
            "required": false,
            "description": "Timestamp du match (Unix)"
        },
        "SC": {
            "type": "object",
            "required": false,
            "description": "Score et statut du match"
        },
        "E": {
            "type": "array",
            "required": false,
            "description": "Cotes principales (T=type, C=cote, P=paramètre, B=blocked)"
        },
        "AE": {
            "type": "array",
            "required": false,
            "description": "Cotes additionnelles par groupe (G=groupe, ME=liste de cotes)"
        }
    },
    "example": {
        "I": "734915710",
        "O1": "Barcelone",
        "O2": "Galatasaray",
        "L": "FC 26. 5x5 Rush. Superligue",
        "S": 1783516200,
        "SC": {"FS": {"S1": 4, "S2": 3}},
        "E": [
            {"T": 1, "C": 1.096},
            {"T": 2, "C": 6.14},
            {"T": 3, "C": 30}
        ]
    }
}

# ─────────────────────────────────────────
# FORMAT DE SORTIE (Réponses de l'API pour les plateformes)
# ─────────────────────────────────────────

OUTPUT_FORMAT = {
    "description": "Format JSON pour les réponses de prédiction",
    "structure": {
        "success": {
            "type": "boolean",
            "description": "Indique si la prédiction a réussi"
        },
        "match_id": {
            "type": "string",
            "description": "Identifiant du match"
        },
        "team_home": {
            "type": "string",
            "description": "Équipe domicile"
        },
        "team_away": {
            "type": "string",
            "description": "Équipe extérieur"
        },
        "league": {
            "type": "string",
            "description": "Nom de la ligue"
        },
        "family": {
            "type": "string",
            "description": "Famille de la ligue (HIGHSCORE, RUSH, PENALTY, CLASSIC, CHAMPIONS, WORLD)"
        },
        "predictions": {
            "type": "object",
            "description": "Prédictions pour différents types de paris",
            "subfields": {
                "match_result": {
                    "type": "object",
                    "description": "Prédiction du résultat du match (1X2)",
                    "fields": {
                        "prediction": {
                            "type": "string",
                            "values": ["home_win", "draw", "away_win"],
                            "description": "Résultat prédit"
                        },
                        "confidence": {
                            "type": "float",
                            "range": [0, 1],
                            "description": "Niveau de confiance (0-1)"
                        },
                        "probabilities": {
                            "type": "object",
                            "fields": {
                                "home_win": {"type": "float", "description": "Probabilité victoire domicile"},
                                "draw": {"type": "float", "description": "Probabilité match nul"},
                                "away_win": {"type": "float", "description": "Probabilité victoire extérieur"}
                            }
                        }
                    }
                },
                "total_goals": {
                    "type": "object",
                    "description": "Prédiction du total de buts",
                    "fields": {
                        "predicted": {
                            "type": "float",
                            "description": "Nombre de buts prédit"
                        },
                        "platform_value": {
                            "type": "float",
                            "description": "Valeur la plus proche disponible sur la plateforme"
                        },
                        "confidence": {
                            "type": "float",
                            "range": [0, 1],
                            "description": "Niveau de confiance"
                        }
                    }
                },
                "total_parity": {
                    "type": "object",
                    "description": "Prédiction de la parité du total (pair/impair)",
                    "fields": {
                        "prediction": {
                            "type": "string",
                            "values": ["even", "odd"],
                            "description": "Parité prédite"
                        },
                        "confidence": {
                            "type": "float",
                            "range": [0, 1],
                            "description": "Niveau de confiance"
                        }
                    }
                },
                "over_under": {
                    "type": "object",
                    "description": "Prédiction Over/Under",
                    "fields": {
                        "threshold": {
                            "type": "float",
                            "description": "Seuil de buts (adapté selon la famille)"
                        },
                        "prediction": {
                            "type": "string",
                            "values": ["over", "under"],
                            "description": "Prédiction Over ou Under"
                        },
                        "confidence": {
                            "type": "float",
                            "range": [0, 1],
                            "description": "Niveau de confiance"
                        },
                        "probabilities": {
                            "type": "object",
                            "fields": {
                                "under": {"type": "float", "description": "Probabilité Under"},
                                "over": {"type": "float", "description": "Probabilité Over"}
                            }
                        }
                    }
                },
                "btts": {
                    "type": "object",
                    "description": "Both Teams To Score",
                    "fields": {
                        "prediction": {
                            "type": "string",
                            "values": ["yes", "no"],
                            "description": "Les deux équipes marquent-elles?"
                        },
                        "confidence": {
                            "type": "float",
                            "range": [0, 1],
                            "description": "Niveau de confiance"
                        },
                        "probabilities": {
                            "type": "object",
                            "fields": {
                                "no": {"type": "float", "description": "Probabilité BTTS No"},
                                "yes": {"type": "float", "description": "Probabilité BTTS Yes"}
                            }
                        }
                    }
                }
            }
        },
        "platform_mapping": {
            "type": "object",
            "description": "Mapping vers les options spécifiques de la plateforme",
            "fields": {
                "total_goals": {
                    "type": "object",
                    "fields": {
                        "predicted": {"type": "float", "description": "Valeur prédite"},
                        "platform_value": {"type": "float", "description": "Option plateforme la plus proche"},
                        "platform_name": {"type": "string", "description": "Nom de l'option"}
                    }
                },
                "handicap": {
                    "type": "object",
                    "fields": {
                        "predicted": {"type": "float", "description": "Handicap prédit"},
                        "platform_value": {"type": "float", "description": "Option plateforme la plus proche"},
                        "platform_name": {"type": "string", "description": "Nom de l'option"}
                    }
                }
            }
        },
        "timestamp": {
            "type": "integer",
            "description": "Timestamp de la prédiction"
        }
    },
    "example": {
        "success": True,
        "match_id": "734797802",
        "team_home": "Club Atlético de Madrid",
        "team_away": "Porto",
        "league": "FC 26. 5x5 Rush. Superligue",
        "family": "RUSH",
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
                "platform_value": 7.5,
                "confidence": 0.85
            },
            "total_parity": {
                "prediction": "even",
                "confidence": 0.55
            },
            "over_under": {
                "threshold": 6.5,
                "prediction": "over",
                "confidence": 0.92,
                "probabilities": {
                    "under": 0.08,
                    "over": 0.92
                }
            },
            "btts": {
                "prediction": "yes",
                "confidence": 0.95,
                "probabilities": {
                    "no": 0.05,
                    "yes": 0.95
                }
            }
        },
        "platform_mapping": {
            "total_goals": {
                "predicted": 7.4,
                "platform_value": 7.5,
                "platform_name": "Total Goals"
            },
            "handicap": {
                "predicted": 0.5,
                "platform_value": 0.5,
                "platform_name": "Handicap"
            }
        },
        "timestamp": 1783473000
    }
}

# ─────────────────────────────────────────
# ENDPOINTS API
# ─────────────────────────────────────────

API_ENDPOINTS = {
    "/health": {
        "method": "GET",
        "description": "Vérifie la santé de l'API",
        "response": {
            "status": "string",
            "models_loaded": "integer",
            "leagues_supported": "integer"
        }
    },
    "/predict": {
        "method": "POST",
        "description": "Prédiction pour un match",
        "request": INPUT_FORMAT,
        "response": OUTPUT_FORMAT
    },
    "/predict/batch": {
        "method": "POST",
        "description": "Prédictions pour plusieurs matchs",
        "request": {
            "matches": [INPUT_FORMAT["example"]]
        },
        "response": {
            "success": "boolean",
            "predictions": [OUTPUT_FORMAT["example"]]
        }
    },
    "/leagues": {
        "method": "GET",
        "description": "Liste des ligues supportées",
        "response": {
            "total": "integer",
            "leagues": [
                {
                    "name": "string",
                    "family": "string",
                    "models_available": ["string"]
                }
            ]
        }
    },
    "/model/{league_name}": {
        "method": "GET",
        "description": "Informations sur le modèle d'une ligue",
        "response": {
            "league": "string",
            "family": "string",
            "models": {
                "match_result": {"type": "string", "accuracy": "float"},
                "total_goals": {"type": "string", "accuracy": "float"},
                "total_parity": {"type": "string", "accuracy": "float"}
            }
        }
    }
}

# ─────────────────────────────────────────
# CODES D'ERREUR
# ─────────────────────────────────────────

ERROR_CODES = {
    400: {
        "code": "BAD_REQUEST",
        "message": "Format de requête invalide"
    },
    404: {
        "code": "LEAGUE_NOT_FOUND",
        "message": "Ligue non trouvée ou non supportée"
    },
    500: {
        "code": "INTERNAL_ERROR",
        "message": "Erreur interne du serveur"
    },
    503: {
        "code": "MODEL_NOT_LOADED",
        "message": "Modèle non chargé pour cette ligue"
    }
}

# ─────────────────────────────────────────
# FONCTIONS D'AFFICHAGE
# ─────────────────────────────────────────

def print_integration_spec():
    """Affiche la spécification d'intégration"""
    print("=" * 80)
    print("SPÉCIFICATION D'INTÉGRATION API FIFA PREDICTION")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("FORMAT D'ENTRÉE (Requête des plateformes)")
    print("=" * 80)
    print(json.dumps(INPUT_FORMAT, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("FORMAT DE SORTIE (Réponse de l'API)")
    print("=" * 80)
    print(json.dumps(OUTPUT_FORMAT, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("ENDPOINTS API")
    print("=" * 80)
    print(json.dumps(API_ENDPOINTS, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("CODES D'ERREUR")
    print("=" * 80)
    print(json.dumps(ERROR_CODES, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print_integration_spec()
