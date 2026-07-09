"""
Mapping des Noms de Ligues - Plateforme vers FIFA
================================================

Ce fichier contient le mapping entre les noms de ligues utilisés par la plateforme
et les noms de ligues FIFA utilisés dans nos modèles.

Author: SOLITAIRE HACK
Version: 1.0
Date: 2026-07-09
"""

import json

# Mapping officiel FURY X ONE des ligues EA SPORTS FC
LEAGUE_NAME_MAPPING = {
    # 🟢 PENALTY
    "Penalty": "Penalty",
    "FIFA23. Penalty": "FIFA23__Penalty",
    "FC24. Penalty": "FC24__Penalty",
    "FC25. Penalty": "FC25__Penalty",
    "FC26. Penalty": "FC26__Penalty",
    
    # 🔴 HIGHSCORE
    "FC 24. 4x4. Championnat d'Angleterre": "FC_24__4x4__Championnat_d'Angleterre",
    "FC 25. 3x3. Ligue de conférence": "FC_25__3x3__Ligue_de_conférence",
    
    # 🟣 RUSH
    "FC 26. 5x5 Rush. Superligue": "FC_26__5x5_Rush__Superligue",
    
    # 🔵 CLASSIC
    "FC 25. Championnat d'Allemagne": "FC_25__Championnat_d'Allemagne",
    "FC 25. Championnat d'Angleterre": "FC_25__Championnat_d'Angleterre",
    "FC 25. Championnat d'Espagne": "FC_25__Championnat_d'Espagne",
    "FC 25. Italy Championship": "FC_25__Italy_Championship",
    "FC 25. Ligue européenne": "FC_25__Ligue_européenne",
    "FC 25. Champions League": "FC_25__Champions_League",
    "FC 26. Champions League": "FC_26__Champions_League",
    "FC 26. Championnat du monde": "FC_26__Championnat_du_monde",
    "FC 26. Spain Championship": "FC_26__Spain_Championship",
    "World Cup 2026. Simulation": "World_Cup_2026__Simulation",
    
    # Variations de noms (compatibilité)
    "Ligue 1": "FC_25__Championnat_d'Angleterre",
    "Premier League": "FC_25__Championnat_d'Angleterre",
    "La Liga": "FC_25__Championnat_d'Espagne",
    "Bundesliga": "FC_25__Championnat_d'Allemagne",
    "Serie A": "FC_25__Italy_Championship",
    "Champions League": "FC_26__Champions_League",
    "Europa League": "FC_25__Ligue_européenne",
    "World Cup": "FC_26__Championnat_du_monde",
}

# Mapping officiel FURY X ONE des catégories
LEAGUE_CATEGORY_MAPPING = {
    "Penalty": {
        "Penalty",
        "FIFA23. Penalty",
        "FC24. Penalty",
        "FC25. Penalty",
        "FC26. Penalty",
    },
    "HighScore": {
        "FC 24. 4x4. Championnat d'Angleterre",
        "FC 25. 3x3. Ligue de conférence",
    },
    "Rush": {
        "FC 26. 5x5 Rush. Superligue",
    },
    "Classic": {
        "FC 25. Championnat d'Allemagne",
        "FC 25. Championnat d'Angleterre",
        "FC 25. Championnat d'Espagne",
        "FC 25. Italy Championship",
        "FC 25. Ligue européenne",
        "FC 25. Champions League",
        "FC 26. Champions League",
        "FC 26. Championnat du monde",
        "FC 26. Spain Championship",
        "World Cup 2026. Simulation",
    }
}

def get_league_category(league_name):
    """
    Retourne la catégorie de la ligue selon le mapping officiel FURY X ONE
    
    Args:
        league_name (str): Nom de la ligue
        
    Returns:
        str: Catégorie (Penalty, HighScore, Rush, Classic, ou Unknown)
    """
    for category, leagues in LEAGUE_CATEGORY_MAPPING.items():
        if league_name in leagues:
            return category
    return "Unknown"

def normalize_league_name(platform_league_name):
    """
    Normalise le nom de la ligue de la plateforme vers le nom FIFA
    
    Args:
        platform_league_name (str): Nom de la ligue depuis la plateforme
        
    Returns:
        str: Nom de la ligue FIFA correspondant
    """
    if not platform_league_name:
        return "FC 26. 5x5 Rush. Superligue"  # Valeur par défaut
    
    # Recherche exacte
    if platform_league_name in LEAGUE_NAME_MAPPING:
        return LEAGUE_NAME_MAPPING[platform_league_name]
    
    # Recherche partielle (insensible à la casse)
    platform_lower = platform_league_name.lower()
    for key, value in LEAGUE_NAME_MAPPING.items():
        if key.lower() in platform_lower or platform_lower in key.lower():
            return value
    
    # Si pas de correspondance, retourner le nom original
    return platform_league_name

def parse_platform_payload(payload):
    """
    Parse et normalise le payload envoyé par la plateforme
    
    Args:
        payload (dict): Payload envoyé par la plateforme
        
    Returns:
        dict: Payload normalisé pour notre API
    """
    normalized = {
        'I': payload.get('I', payload.get('match_id', payload.get('id', ''))),
        'O1': payload.get('O1', payload.get('team_home', payload.get('teamHome', payload.get('home_team', payload.get('team1', ''))))),
        'O2': payload.get('O2', payload.get('team_away', payload.get('teamAway', payload.get('away_team', payload.get('team2', ''))))),
        'L': normalize_league_name(payload.get('L', payload.get('league', ''))),
        'S': payload.get('S', payload.get('timestamp', payload.get('startTimeTimestamp', None))),
        'SC': payload.get('SC', None),  # Score actuel (optionnel)
    }
    
    # Normaliser les marchés principaux (E)
    E = payload.get('E', payload.get('markets', []))
    normalized_E = []
    for market in E:
        normalized_market = {
            'T': market.get('T'),
            'C': market.get('C'),
        }
        # Champs optionnels
        if 'P' in market and market['P'] is not None:
            normalized_market['P'] = market['P']
        if 'B' in market and market['B'] is not None:
            normalized_market['B'] = market['B']
        if 'G' in market and market['G'] is not None:
            normalized_market['G'] = market['G']
        normalized_E.append(normalized_market)
    normalized['E'] = normalized_E
    
    # Normaliser les marchés avancés (AE) - structure imbriquée
    AE = payload.get('AE', payload.get('advancedMarkets', payload.get('advancedMarkets', {}).get('advancedMarkets', [])))
    normalized_AE = []
    
    for ae_group in AE:
        if isinstance(ae_group, dict):
            # Structure imbriquée: {G: X, ME: [...]}
            if 'G' in ae_group and 'ME' in ae_group:
                for market in ae_group['ME']:
                    normalized_market = {
                        'T': market.get('T'),
                        'C': market.get('C'),
                    }
                    if 'P' in market and market['P'] is not None:
                        normalized_market['P'] = market['P']
                    if 'B' in market and market['B'] is not None:
                        normalized_market['B'] = market['B']
                    if 'G' in market and market['G'] is not None:
                        normalized_market['G'] = market['G']
                    else:
                        normalized_market['G'] = ae_group['G']  # Hériter du groupe parent
                    normalized_AE.append(normalized_market)
            else:
                # Structure plate (déjà normalisée)
                normalized_AE.append(ae_group)
    
    normalized['AE'] = normalized_AE
    
    return normalized

if __name__ == "__main__":
    # Test du mapping
    test_names = [
        "Ligue 1",
        "Premier League",
        "Champions League",
        "FC 26. 5x5 Rush. Superligue",
        "Unknown League"
    ]
    
    print("=== TEST DU MAPPING DE LIGUES ===")
    for name in test_names:
        normalized = normalize_league_name(name)
        print(f"{name} -> {normalized}")
    
    # Test du parsing de payload
    print("\n=== TEST DU PARSING DE PAYLOAD ===")
    test_payload = {
        "I": "match_12345",
        "O1": "PSG",
        "O2": "Lyon",
        "L": "Ligue 1",
        "S": 1719504000,
        "SC": None,
        "E": [
            {"T": 1, "C": 1.85, "P": None, "B": "888starz", "G": 1}
        ],
        "AE": [
            {
                "G": 2,
                "ME": [
                    {"T": 7, "C": 1.95, "P": -1.0, "B": "888starz"}
                ]
            }
        ]
    }
    
    normalized = parse_platform_payload(test_payload)
    print(json.dumps(normalized, indent=2, ensure_ascii=False))
