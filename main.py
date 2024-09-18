"""Module for finding nearby tourist attractions using Google Maps API."""

import math
import os
from typing import List
from fastapi import FastAPI, HTTPException
import googlemaps
from haversine import haversine, Unit
from pydantic import BaseModel

app = FastAPI()

# Get Google Maps API key from environment variable
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Debug: Print the API key
print(f"Using Google Maps API Key: {GOOGLE_MAPS_API_KEY}")


class Attraction(BaseModel):
    """Class representing an attraction."""
    name: str
    address: str
    distance_km: float
    bearing_degrees: int


def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing between two points.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: Bearing in degrees from the first point to the second point.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (
        math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    )
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing


def find_attractions(
    lat, lon, language="pl", radius=2000, type="tourist_attraction"
) -> List[Attraction]:
    """
    Find nearby tourist attractions using Google Maps API.

    Args:
        lat (float): Latitude of the starting point.
        lon (float): Longitude of the starting point.
        language (str, optional): Language for the results. Defaults to "pl".
        radius (int, optional): Search radius in meters. Defaults to 2000.
        type (str, optional): Type of place to search for. Defaults to "tourist_attraction".

    Returns:
        List[Attraction]: List of nearby attractions sorted by distance.
    """
    # Debug: Print the API key again before making the API call
    print(f"Making API call with key: {GOOGLE_MAPS_API_KEY}")

    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("Google Maps API key is not set")

    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    start_location = (lat, lon)
    places_result = gmaps.places_nearby(
        location=start_location, radius=radius, type=type, language=language
    )

    attractions = []
    for place in places_result.get("results", []):
        if place.get("permanently_closed", False):
            continue
        place_location = (
            place["geometry"]["location"]["lat"],
            place["geometry"]["location"]["lng"],
        )
        distance = haversine(start_location, place_location, unit=Unit.KILOMETERS)
        bearing = calculate_bearing(lat, lon, place_location[0], place_location[1])
        name = place.get("name")
        vicinity = place.get("vicinity")
        attraction = Attraction(
            name=name,
            address=vicinity,
            distance_km=round(distance, 2),
            bearing_degrees=int(bearing),
        )
        attractions.append(attraction)

    # Sorting by distance
    attractions.sort(key=lambda x: x.distance_km)
    return attractions


@app.get("/attractions/", response_model=List[Attraction])
async def get_attractions(lat: float, lon: float) -> List[Attraction]:
    """
    Get nearby tourist attractions.

    Args:
        lat (float): Latitude of the starting point.
        lon (float): Longitude of the starting point.

    Returns:
        List[Attraction]: List of nearby attractions sorted by distance.

    Raises:
        HTTPException: If there's an error during the process.
    """
    try:
        return find_attractions(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
