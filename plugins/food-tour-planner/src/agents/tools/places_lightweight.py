"""Lightweight Google Places tools for DeepAgent - minimal data for fast responses."""

import os
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from googlemaps import Client as GoogleMapsClient


class PlacesLightweightTools:
    """Lightweight tools for Google Places API - returns only essential info."""
    
    def __init__(self, api_key: str):
        self.client = GoogleMapsClient(key=api_key)
        self.api_key = api_key
    
    @staticmethod
    def format_place_light(place: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Format place with minimal essential data."""
        photos = []
        if 'photos' in place and len(place['photos']) > 0:
            for photo in place['photos'][:2]:
                photo_ref = photo.get('photo_reference')
                if photo_ref:
                    photos.append({
                        'url': f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={api_key}",
                        'attribution': photo.get('html_attributions', [''])[0] if photo.get('html_attributions') else None
                    })
        
        reviews = []
        if 'reviews' in place:
            for review in place['reviews'][:3]:
                reviews.append({
                    'author': review.get('author_name'),
                    'rating': review.get('rating'),
                    'text': review.get('text', '')[:300],
                    'time': review.get('relative_time_description')
                })
        
        return {
            'name': place.get('name'),
            'place_id': place.get('place_id'),
            'address': place.get('formatted_address') or place.get('vicinity'),
            'location': place.get('geometry', {}).get('location'),
            'rating': place.get('rating'),
            'total_reviews': place.get('user_ratings_total', 0),
            'price_level': '$' * place.get('price_level', 0) if place.get('price_level') else None,
            'types': place.get('types', [])[:3],
            'website': place.get('website'),
            'phone': place.get('formatted_phone_number'),
            'is_open': place.get('current_opening_hours', {}).get('open_now') or place.get('opening_hours', {}).get('open_now'),
            'photos': photos,
            'reviews': reviews
        }
    
    def get_tools(self):
        """Return list of tools for the agent."""
        api_key = self.api_key
        client = self.client
        format_func = self.format_place_light
        
        @tool
        def search_restaurants_nearby(lat: float, lng: float, radius: int = 500, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
            """
            Search for restaurants near a location. Returns lightweight data with name, address,
            rating, 2 photos, 3 reviews, and website.
            
            Args:
                lat: Latitude of search center
                lng: Longitude of search center
                radius: Search radius in meters (default 500, max 2000)
                keyword: Optional keyword to filter results (e.g., "italian", "seafood")
            
            Returns:
                List of restaurants with essential information
            """
            try:
                params = {
                    'location': (lat, lng),
                    'radius': min(radius, 2000),
                    'type': 'restaurant'
                }
                if keyword:
                    params['keyword'] = keyword
                
                result = client.places_nearby(**params)
                places = result.get('results', [])[:10]
                
                detailed_places = []
                for place in places:
                    try:
                        # Use the Place Details API with proper field specification
                        details = client.place(
                            place_id=place['place_id'],
                            fields=[
                                'name',
                                'place_id', 
                                'formatted_address',
                                'geometry',
                                'rating',
                                'user_ratings_total',
                                'price_level',
                                'types',
                                'website',
                                'formatted_phone_number',
                                'opening_hours',  # Use opening_hours instead of current_opening_hours for googlemaps library
                                'photo',
                                'review'
                            ]
                        )
                        detailed_places.append(format_func(details['result'], api_key))
                    except Exception as e:
                        detailed_places.append({
                            'name': place.get('name'),
                            'address': place.get('vicinity'),
                            'rating': place.get('rating'),
                            'error': f'Details unavailable: {str(e)}'
                        })
                
                return detailed_places
            except Exception as e:
                return [{'error': f'Search failed: {str(e)}'}]
        
        @tool
        def search_bars_cafes_nearby(lat: float, lng: float, radius: int = 500, place_type: str = "bar") -> List[Dict[str, Any]]:
            """
            Search for bars, cafes, or nightlife near a location.
            
            Args:
                lat: Latitude of search center
                lng: Longitude of search center
                radius: Search radius in meters (default 500, max 2000)
                place_type: Type of place ("bar", "cafe", "night_club")
            
            Returns:
                List of establishments with essential information
            """
            try:
                result = client.places_nearby(
                    location=(lat, lng),
                    radius=min(radius, 2000),
                    type=place_type
                )
                places = result.get('results', [])[:10]
                
                detailed_places = []
                for place in places:
                    try:
                        # Use the Place Details API with proper field specification
                        details = client.place(
                            place_id=place['place_id'],
                            fields=[
                                'name',
                                'place_id', 
                                'formatted_address',
                                'geometry',
                                'rating',
                                'user_ratings_total',
                                'price_level',
                                'types',
                                'website',
                                'formatted_phone_number',
                                'opening_hours',  # Use opening_hours instead of current_opening_hours for googlemaps library
                                'photo',
                                'review'
                            ]
                        )
                        detailed_places.append(format_func(details['result'], api_key))
                    except:
                        detailed_places.append({
                            'name': place.get('name'),
                            'address': place.get('vicinity'),
                            'rating': place.get('rating')
                        })
                
                return detailed_places
            except Exception as e:
                return [{'error': f'Search failed: {str(e)}'}]
        
        @tool
        def geocode_location(address: str) -> Dict[str, Any]:
            """
            Convert an address or place name to coordinates.
            
            Args:
                address: Address or place name to geocode
            
            Returns:
                Location data with lat/lng and formatted address
            """
            try:
                result = client.geocode(address)
                if result:
                    location = result[0]
                    return {
                        'address': location['formatted_address'],
                        'location': location['geometry']['location'],
                        'place_id': location['place_id'],
                        'types': location.get('types', [])
                    }
                return {'error': 'Location not found'}
            except Exception as e:
                return {'error': f'Geocoding failed: {str(e)}'}
        
        return [search_restaurants_nearby, search_bars_cafes_nearby, geocode_location]

