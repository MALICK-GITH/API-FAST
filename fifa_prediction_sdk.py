"""
FIFA Prediction SDK
===================
SDK Python pour intégrer l'API de prédiction FIFA (Flask)

Author: SOLITAIRE HACK
Version: 1.0 - Production Ready
"""

import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

@dataclass
class MatchData:
    """Données d'un match pour prédiction"""
    team_home: str
    team_away: str
    league: str
    match_id: Optional[str] = None
    status: Optional[str] = None
    timestamp: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convertit en format compatible avec l'API"""
        return {
            "O1": self.team_home,
            "O2": self.team_away,
            "L": self.league,
            "I": self.match_id,
            "ST": self.status,
            "S": self.timestamp
        }

@dataclass
class PredictionResult:
    """Résultat d'une prédiction"""
    success: bool
    match_id: str
    team_home: str
    team_away: str
    league: str
    family: str
    match_result: Optional[Dict[str, Any]] = None
    over_under: Optional[Dict[str, Any]] = None
    btts: Optional[Dict[str, Any]] = None
    platform_mapping: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[int] = None
    
    @classmethod
    def from_response(cls, response: Dict) -> 'PredictionResult':
        """Crée un PredictionResult depuis la réponse de l'API"""
        if 'error' in response:
            return cls(
                success=False,
                match_id=response.get('match_id', 'unknown'),
                team_home='',
                team_away='',
                league='',
                family='UNKNOWN',
                error=response['error']
            )
        
        return cls(
            success=True,
            match_id=response.get('match_id', 'unknown'),
            team_home=response.get('team_home', ''),
            team_away=response.get('team_away', ''),
            league=response.get('league', ''),
            family=response.get('family', 'UNKNOWN'),
            match_result=response.get('match_result'),
            over_under=response.get('over_under'),
            btts=response.get('btts'),
            platform_mapping=response.get('platform_mapping'),
            timestamp=response.get('timestamp')
        )
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            "success": self.success,
            "match_id": self.match_id,
            "team_home": self.team_home,
            "team_away": self.team_away,
            "league": self.league,
            "family": self.family,
            "match_result": self.match_result,
            "over_under": self.over_under,
            "btts": self.btts,
            "platform_mapping": self.platform_mapping,
            "error": self.error,
            "timestamp": self.timestamp
        }

# ─────────────────────────────────────────
# CLIENT SDK
# ─────────────────────────────────────────

class FIFAPredictionClient:
    """Client SDK pour FIFA Prediction API (Flask)"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        """
        Initialise le client SDK
        
        Args:
            base_url: URL de base de l'API (défaut: http://localhost:5000)
            timeout: Timeout des requêtes en secondes (défaut: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Effectue une requête HTTP"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Méthode non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Erreur de requête: {str(e)}",
                "match_id": "unknown"
            }
    
    def health_check(self) -> Dict:
        """
        Vérifie la santé de l'API
        
        Returns:
            Dict: Statut de santé de l'API
        """
        return self._request("GET", "/health")
    
    def predict_match(self, match_data: MatchData) -> PredictionResult:
        """
        Génère une prédiction pour un match
        
        Args:
            match_data: Données du match (MatchData)
        
        Returns:
            PredictionResult: Résultat de la prédiction
        """
        data = match_data.to_dict()
        response = self._request("POST", "/predict", data)
        return PredictionResult.from_response(response)
    
    def predict_batch(self, matches: List[MatchData]) -> List[PredictionResult]:
        """
        Génère des prédictions pour plusieurs matchs
        
        Args:
            matches: Liste de données de matchs
        
        Returns:
            List[PredictionResult]: Résultats des prédictions
        """
        results = []
        for match in matches:
            result = self.predict_match(match)
            results.append(result)
        return results
    
    def get_team_stats(self, team_name: str) -> Dict:
        """
        Récupère les statistiques d'une équipe
        
        Args:
            team_name: Nom de l'équipe
        
        Returns:
            Dict: Statistiques de l'équipe
        """
        return self._request("GET", f"/team_stats/{team_name}")
    
    def close(self):
        """Ferme la session HTTP"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# ─────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────

def parse_json_match(json_data: Dict) -> MatchData:
    """
    Parse un match depuis le format JSON du système
    
    Args:
        json_data: Données JSON du match
    
    Returns:
        MatchData: Données du match structurées
    """
    return MatchData(
        team_home=json_data.get('O1', ''),
        team_away=json_data.get('O2', ''),
        league=json_data.get('L', ''),
        match_id=json_data.get('I'),
        status=json_data.get('ST'),
        timestamp=json_data.get('S')
    )

def parse_json_batch(json_data: List[Dict]) -> List[MatchData]:
    """
    Parse plusieurs matchs depuis le format JSON du système
    
    Args:
        json_data: Liste de données JSON de matchs
    
    Returns:
        List[MatchData]: Liste de données de matchs structurées
    """
    return [parse_json_match(match) for match in json_data]

# ─────────────────────────────────────────
# EXEMPLES D'UTILISATION
# ─────────────────────────────────────────

if __name__ == "__main__":
    # Exemple d'utilisation du SDK
    client = FIFAPredictionClient(base_url="http://localhost:5000")
    
    try:
        # Vérification de santé
        health = client.health_check()
        print(f"Santé API: {health}")
        
        # Prédiction simple
        match = MatchData(
            team_home="Club Atlético de Madrid",
            team_away="Porto",
            league="FC 26. 5x5 Rush. Superligue",
            match_id="734797802",
            status="Paris avant le début du jeu",
            timestamp=1783473000
        )
        
        prediction = client.predict_match(match)
        print(f"\n=== PRÉDICTION ===")
        print(f"Match: {prediction.team_home} vs {prediction.team_away}")
        print(f"Ligue: {prediction.league}")
        print(f"Famille: {prediction.family}")
        print(f"Résultat: {prediction.match_result}")
        print(f"Over/Under: {prediction.over_under}")
        print(f"BTTS: {prediction.btts}")
        print(f"Mapping Plateforme: {prediction.platform_mapping}")
        
        # Prédiction batch
        matches = [
            MatchData(
                team_home="Club Atlético de Madrid",
                team_away="Porto",
                league="FC 26. 5x5 Rush. Superligue",
                match_id="734797802"
            ),
            MatchData(
                team_home="Galatasaray",
                team_away="Bayer 04",
                league="FC 26. 5x5 Rush. Superligue",
                match_id="734796647"
            )
        ]
        
        predictions = client.predict_batch(matches)
        print(f"\n=== PRÉDICTIONS BATCH ===")
        for pred in predictions:
            if pred.success:
                print(f"{pred.team_home} vs {pred.team_away}: {pred.match_result['prediction']}")
            else:
                print(f"Erreur: {pred.error}")
        
    finally:
        client.close()
