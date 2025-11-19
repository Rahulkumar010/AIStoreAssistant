import requests
from config import config
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SerpApiClient:
    BASE_URL = "https://serpapi.com/search.json"

    def __init__(self):
        if not config.is_serpapi_configured():
            logger.warning("Serp API is not configured. Please set environment variables.")
            self.api_key = None
        else:
            self.api_key = config.SERP_API_KEY

        self.params = {
            "api_key": self.api_key,
            "hl": "en",
        }

    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def _request(self, **kwargs) -> Optional[Dict]:
        """Internal helper to send GET requests to SerpApi."""
        try:
            response = requests.get(self.BASE_URL, params=kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from SerpApi: {e}")
            return None

    def fetch_sainsbury_place(self, location: str) -> Optional[Dict]:
        """Fetch places for the given location and filter for Sainsbury if present."""
        if not self.is_configured():
            return None

        if "sainsbury" not in location.lower():
            location = f"Sainsbury, {location}"

        params = {
            **self.params,
            "engine": "google_maps",
            "q": location,
        }

        results = self._request(**params)
        if not results:
            return None

        places = results.get("local_results", [])
        if not places:
            places = [results.get("place_results", {})]

        for place in places:
            if "sainsbury" in place.get("title", "").lower():
                return {
                    "title": place.get("title"),
                    "place_id": place.get("place_id"),
                    "data_id": place.get("data_id"),
                    "data_cid": place.get("data_cid"),
                }

        first = places[0]
        return {
            "title": first.get("title"),
            "place_id": first.get("place_id"),
            "data_id": first.get("data_id"),
            "data_cid": first.get("data_cid"),
        }

    def fetch_reviews(self, location: str, data_id: Optional[str] = None) -> Optional[Dict]:
        """Fetch reviews for the place using data_id via google_maps_reviews engine."""
        if not self.is_configured():
            return None
        if data_id is None:
            data_id = self.fetch_sainsbury_place(location=location)['data_id']

        params = {
            **self.params,
            "engine": "google_maps_reviews",
            "data_id": data_id,
        }

        results = self._request(**params)
        if not results:
            return None

        return results.get("reviews", [])

# Global instance
serpapi_client = SerpApiClient()
