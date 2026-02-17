"""
Location Service

Provides reverse geocoding and elevation data for coordinates.
Uses free and open APIs:
- Nominatim (OpenStreetMap) for address lookup
- Open-Elevation API for altitude data
"""
import logging
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LocationService:
    """Service for getting location metadata from coordinates"""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
    ELEVATION_URL = "https://api.open-elevation.com/api/v1/lookup"

    # Required by Nominatim API
    USER_AGENT = "TwinScale-Lite/1.0"

    def __init__(self):
        """Initialize location service"""
        self.timeout = 10.0

    async def get_location_info(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get location information (address + elevation) for given coordinates

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with address and altitude information
        """
        result = {
            "latitude": latitude,
            "longitude": longitude,
            "address": None,
            "altitude": None,
            "address_components": None,
        }

        # Get address from Nominatim
        try:
            address_data = await self._get_address(latitude, longitude)
            if address_data:
                result["address"] = address_data.get("display_name")
                result["address_components"] = address_data.get("address", {})
        except Exception as e:
            logger.warning(f"Failed to get address for {latitude},{longitude}: {e}")

        # Get elevation
        try:
            altitude = await self._get_elevation(latitude, longitude)
            if altitude is not None:
                result["altitude"] = altitude
        except Exception as e:
            logger.warning(f"Failed to get elevation for {latitude},{longitude}: {e}")

        return result

    async def _get_address(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get address from Nominatim reverse geocoding

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Address data from Nominatim or None
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1,
        }

        headers = {
            "User-Agent": self.USER_AGENT
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                self.NOMINATIM_URL,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def _get_elevation(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[float]:
        """
        Get elevation from Open-Elevation API

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Elevation in meters or None
        """
        params = {
            "locations": f"{latitude},{longitude}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                self.ELEVATION_URL,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Extract elevation from response
            results = data.get("results", [])
            if results and len(results) > 0:
                return results[0].get("elevation")

        return None


__all__ = ["LocationService"]
