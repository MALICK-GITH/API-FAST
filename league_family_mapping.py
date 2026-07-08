"""
Mapping des familles de ligues FIFA
Basé sur l'analyse des scores et caractéristiques des ligues
"""

# Mapping des ligues vers leur famille selon les caractéristiques
LEAGUE_FAMILY_MAPPING = {
    # HIGHSCORE: Ligues avec moyenne de buts > 10
    "HIGHSCORE": [
        "FC 25. 3x3. Ligue de conférence",
        "FC 24. 4x4. Championnat d'Angleterre",
        "FIFA23. Penalty"
    ],
    
    # RUSH: Ligues avec moyenne de buts 6-10
    "RUSH": [
        "FC24. Penalty",
        "FC 26. 5x5 Rush. Superligue",
        "FC25. Penalty",
        "FC26. Penalty"
    ],
    
    # PENALTY: Ligues de penalties (moyenne ~5 buts)
    "PENALTY": [
        "Penalty"
    ],
    
    # CLASSIC: Ligues classiques (moyenne 3-6 buts)
    "CLASSIC": [
        "FC 25. Championnat d'Allemagne",
        "FC 25. Championnat d'Angleterre",
        "FC 25. Championnat d'Espagne",
        "FC 26. Spain Championship",
        "FC 25. Champions League",
        "FC 25. Italy Championship",
        "FC 25. Ligue européenne"
    ],
    
    # CHAMPIONS: Ligues de champions (moyenne ~3.5 buts)
    "CHAMPIONS": [
        "FC 26. Champions League"
    ],
    
    # WORLD: Ligues internationales (moyenne ~3.5 buts)
    "WORLD": [
        "FC 26. Championnat du monde",
        "World Cup 2026. Simulation"
    ]
}

# Options de paris spécifiques par famille
FAMILY_OPTIONS = {
    "HIGHSCORE": {
        "avg_goals": 15.0,
        "has_draw": True,
        "over_under_threshold": 12.0,
        "handicap_range": [-8, 8],
        "total_goals_range": [10, 25]
    },
    "RUSH": {
        "avg_goals": 7.5,
        "has_draw": True,
        "over_under_threshold": 6.5,
        "handicap_range": [-4, 4],
        "total_goals_range": [2.5, 9.5]
    },
    "PENALTY": {
        "avg_goals": 5.0,
        "has_draw": True,
        "over_under_threshold": 4.5,
        "handicap_range": [-4, 4],
        "total_goals_range": [2, 15]
    },
    "CLASSIC": {
        "avg_goals": 3.2,
        "has_draw": True,
        "over_under_threshold": 2.5,
        "handicap_range": [-3, 3],
        "total_goals_range": [0, 9]
    },
    "CHAMPIONS": {
        "avg_goals": 3.5,
        "has_draw": True,
        "over_under_threshold": 2.5,
        "handicap_range": [-3.5, 3.5],
        "total_goals_range": [1.5, 5.5]
    },
    "WORLD": {
        "avg_goals": 3.5,
        "has_draw": True,
        "over_under_threshold": 2.5,
        "handicap_range": [-2.5, 2.5],
        "total_goals_range": [1.5, 5.5]
    }
}

def get_league_family(league_name):
    """
    Retourne la famille d'une ligue donnée
    Returns: 'UNKNOWN' si la ligue n'est pas dans le mapping
    """
    for family, leagues in LEAGUE_FAMILY_MAPPING.items():
        if league_name in leagues:
            return family
    return "UNKNOWN"

def get_family_options(family_name):
    """
    Retourne les options de paris pour une famille donnée
    """
    return FAMILY_OPTIONS.get(family_name, FAMILY_OPTIONS["CLASSIC"])

def map_prediction_to_platform(prediction_type, predicted_value, family):
    """
    Mappe une prédiction du modèle à l'option la plus proche disponible sur la plateforme
    pour une famille spécifique
    
    Args:
        prediction_type: Type de prédiction ('handicap', 'total_goals', 'over_under')
        predicted_value: Valeur prédite par le modèle
        family: Famille de ligue (PENALTY, HIGHSCORE, RUSH, CLASSIC, CHAMPIONS, WORLD)
    
    Returns:
        Tuple (option_value, option_name) la plus proche
    """
    if family not in FAMILY_OPTIONS:
        return (None, None)
    
    family_config = FAMILY_OPTIONS[family]
    
    if prediction_type == "handicap":
        options = list(range(family_config["handicap_range"][0], family_config["handicap_range"][1] + 1, 1))
        closest = min(options, key=lambda x: abs(x - predicted_value))
        return (closest, "Handicap")
    
    elif prediction_type == "total_goals":
        options = family_config["total_goals_range"]
        closest = min(options, key=lambda x: abs(x - predicted_value))
        return (closest, "Total Goals")
    
    elif prediction_type == "over_under":
        threshold = family_config["over_under_threshold"]
        return (threshold, "Over/Under")
    
    else:
        return (None, None)

if __name__ == "__main__":
    # Test du mapping
    print("=== TEST DU MAPPING DES LIGUES ===\n")
    
    test_leagues = [
        "FC 26. 5x5 Rush. Superligue",
        "FC 25. Champions League",
        "Penalty",
        "FC 24. 4x4. Championnat d'Angleterre",
        "FC 26. Championnat du monde"
    ]
    
    for league in test_leagues:
        family = get_league_family(league)
        options = get_family_options(family)
        print(f"{league}")
        print(f"  Famille: {family}")
        print(f"  Options: {options}")
        print()
