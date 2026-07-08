"""
Spécification d'Intégration API FIFA Prediction - Format Plateforme
====================================================================
Document définissant les formats d'entrée et de sortie pour l'intégration
avec les plateformes de paris (format exact de la plateforme)

Author: SOLITAIRE HACK
Version: 2.0
"""

import json

# ─────────────────────────────────────────
# FORMAT D'ENTRÉE (Format exact de la plateforme)
# ─────────────────────────────────────────

INPUT_FORMAT = {
    "description": "Format JSON exact de la plateforme pour les requêtes de prédiction",
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
            "required": True,
            "description": "Nom de la ligue/compétition"
        },
        "S": {
            "type": "integer",
            "required": False,
            "description": "Timestamp du match (Unix)"
        },
        "SC": {
            "type": "object",
            "required": False,
            "description": "Score et statut du match (FS=score final, TS=temps restant)"
        },
        "E": {
            "type": "array",
            "required": False,
            "description": "Cotes principales (T=type, C=cote, P=paramètre, B=blocked)"
        },
        "AE": {
            "type": "array",
            "required": False,
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
    "description": "Format JSON pour les réponses de prédiction (compatible plateforme)",
    "structure": {
        "success": {
            "type": "boolean",
            "description": "Indique si la prédiction a réussi"
        },
        "I": {
            "type": "string",
            "description": "Identifiant du match"
        },
        "O1": {
            "type": "string",
            "description": "Équipe domicile"
        },
        "O2": {
            "type": "string",
            "description": "Équipe extérieur"
        },
        "L": {
            "type": "string",
            "description": "Nom de la ligue"
        },
        "predictions": {
            "type": "object",
            "description": "Prédictions pour différents types de paris",
            "fields": {
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
                        }
                    }
                }
            }
        },
        "platform_odds": {
            "type": "object",
            "description": "Cotes de la plateforme",
            "fields": {
                "main": {
                    "type": "object",
                    "description": "Cotes principales",
                    "fields": {
                        "home_win": {"type": "object", "fields": {"value": "float"}},
                        "draw": {"type": "object", "fields": {"value": "float"}},
                        "away_win": {"type": "object", "fields": {"value": "float"}}
                    }
                },
                "over_under": {
                    "type": "array",
                    "description": "Cotes Over/Under"
                },
                "handicap": {
                    "type": "array",
                    "description": "Cotes de handicap"
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
            },
            "over_under": [
                {"type": "over", "threshold": 7.5, "value": 1.504},
                {"type": "under", "threshold": 7.5, "value": 2.5}
            ],
            "handicap": [
                {"type": "home", "handicap": -1.5, "value": 2.565}
            ]
        },
        "timestamp": 1783516200
    }
}

# ─────────────────────────────────────────
# CODES DE COTE (E.T) - Format Plateforme
# ─────────────────────────────────────────

ODD_CODES = {
    "description": "Codes de cote utilisés dans le champ E",
    "codes": {
        "T=1": "Victoire domicile (Home Win)",
        "T=2": "Match nul (Draw)",
        "T=3": "Victoire extérieur (Away Win)",
        "T=4": "No Bet",
        "T=5": "BTTS Non (Both Teams To Score No)",
        "T=6": "BTTS Oui (Both Teams To Score Yes)",
        "T=7": "Handicap domicile (Home Handicap)",
        "T=8": "Handicap extérieur (Away Handicap)",
        "T=9": "Over (Plus de)",
        "T=10": "Under (Moins de)",
        "T=11": "Over/Under (variante)",
        "T=12": "Over/Under (variante)",
        "T=13": "Over/Under (variante)",
        "T=14": "Over/Under (variante)",
        "T=180": "Double Chance",
        "T=181": "Double Chance (variante)"
    }
}

# ─────────────────────────────────────────
# CODES DE GROUPE (AE.G) - Format Plateforme
# ─────────────────────────────────────────

GROUP_CODES = {
    "description": "Codes de groupe utilisés dans le champ AE",
    "codes": {
        "G=2": "Handicap",
        "G=17": "Total Goals"
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
        "description": "Prédiction pour un match (format plateforme)",
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
    print("SPÉCIFICATION D'INTÉGRATION API FIFA PREDICTION - FORMAT PLATEFORME")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("FORMAT D'ENTRÉE (Format exact de la plateforme)")
    print("=" * 80)
    print(json.dumps(INPUT_FORMAT, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("FORMAT DE SORTIE (Réponse de l'API)")
    print("=" * 80)
    print(json.dumps(OUTPUT_FORMAT, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("CODES DE COTE (E.T)")
    print("=" * 80)
    print(json.dumps(ODD_CODES, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("CODES DE GROUPE (AE.G)")
    print("=" * 80)
    print(json.dumps(GROUP_CODES, indent=2, ensure_ascii=False))
    
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
