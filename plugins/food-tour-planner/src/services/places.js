const { Client } = require('@googlemaps/google-maps-services-js');

class PlacesService {
  constructor(apiKey) {
    this.client = new Client({});
    this.apiKey = apiKey;
  }

  /**
   * Search for restaurants near a location (lat/lng or address)
   * @param {Object} params
   * @param {string} params.address - Street address to search near
   * @param {number} params.radius - Search radius in meters (default 500)
   * @param {string} params.type - Place type (default 'restaurant')
   * @returns {Promise<Array>} Array of restaurant results
   */
  async searchRestaurantsByAddress(params) {
    const { address, radius = 500, type = 'restaurant' } = params;

    try {
      // First, geocode the address to get coordinates
      const geocodeResponse = await this.client.geocode({
        params: {
          address: address,
          key: this.apiKey,
        },
      });

      if (!geocodeResponse.data.results.length) {
        throw new Error('Address not found');
      }

      const location = geocodeResponse.data.results[0].geometry.location;

      // Then search for restaurants near those coordinates
      const placesResponse = await this.client.placesNearby({
        params: {
          location: location,
          radius: radius,
          type: type,
          key: this.apiKey,
        },
      });

      return this.formatResults(placesResponse.data.results);
    } catch (error) {
      throw new Error(`Places API error: ${error.message}`);
    }
  }

  /**
   * Search restaurants along a route/path
   * @param {Object} params
   * @param {Array<{lat: number, lng: number}>} params.coordinates - Array of coordinates defining the path
   * @param {number} params.radius - Search radius around each point (default 100)
   * @returns {Promise<Array>} Unique restaurants along the path
   */
  async searchRestaurantsAlongPath(params) {
    const { coordinates, radius = 100 } = params;

    try {
      const allResults = [];
      const seenPlaceIds = new Set();

      // Search near each coordinate point
      for (const coord of coordinates) {
        const placesResponse = await this.client.placesNearby({
          params: {
            location: coord,
            radius: radius,
            type: 'restaurant',
            key: this.apiKey,
          },
        });

        // Deduplicate results
        const results = placesResponse.data.results.filter(place => {
          if (seenPlaceIds.has(place.place_id)) {
            return false;
          }
          seenPlaceIds.add(place.place_id);
          return true;
        });

        allResults.push(...results);
      }

      return this.formatResults(allResults);
    } catch (error) {
      throw new Error(`Places API error: ${error.message}`);
    }
  }

  /**
   * Get detailed information about a specific place
   * @param {string} placeId - Google Place ID
   * @param {Object} options - Optional parameters
   * @param {string} options.language - Language code for reviews (e.g., 'en')
   * @returns {Promise<Object>} Detailed place information
   */
  async getPlaceDetails(placeId, options = {}) {
    try {
      const params = {
        place_id: placeId,
        fields: [
          'name',
          'formatted_address',
          'address_components',
          'geometry',
          'rating',
          'user_ratings_total',
          'price_level',
          'opening_hours',
          'current_opening_hours',
          'photos',
          'types',
          'website',
          'formatted_phone_number',
          'international_phone_number',
          'reviews',
          'editorial_summary',
          'serves_breakfast',
          'serves_lunch',
          'serves_dinner',
          'serves_brunch',
          'serves_vegetarian_food',
          'delivery',
          'dine_in',
          'takeout',
          'reservable',
          'url',
        ],
        key: this.apiKey,
      };

      if (options.language) {
        params.language = options.language;
      }

      const response = await this.client.placeDetails({ params });

      return this.formatPlaceDetails(response.data.result);
    } catch (error) {
      throw new Error(`Place Details API error: ${error.message}`);
    }
  }

  /**
   * Format detailed place data for better consumption
   * @param {Object} place - Raw place details from API
   * @returns {Object} Formatted place details
   */
  formatPlaceDetails(place) {
    return {
      placeId: place.place_id,
      name: place.name,
      address: place.formatted_address,
      location: place.geometry?.location,
      phone: place.formatted_phone_number || place.international_phone_number,
      website: place.website,
      googleMapsUrl: place.url,
      
      rating: {
        score: place.rating,
        totalReviews: place.user_ratings_total,
      },
      
      priceLevel: place.price_level,
      
      types: place.types,
      
      hours: {
        weekdayText: place.opening_hours?.weekday_text || [],
        openNow: place.opening_hours?.open_now,
        periods: place.opening_hours?.periods || [],
      },
      
      services: {
        breakfast: place.serves_breakfast,
        lunch: place.serves_lunch,
        dinner: place.serves_dinner,
        brunch: place.serves_brunch,
        vegetarian: place.serves_vegetarian_food,
        delivery: place.delivery,
        dineIn: place.dine_in,
        takeout: place.takeout,
        reservable: place.reservable,
      },
      
      photos: place.photos?.map(photo => ({
        reference: photo.photo_reference,
        width: photo.width,
        height: photo.height,
        attributions: photo.html_attributions,
      })) || [],
      
      reviews: place.reviews?.map(review => ({
        author: review.author_name,
        authorUrl: review.author_url,
        profilePhoto: review.profile_photo_url,
        rating: review.rating,
        text: review.text,
        time: review.time,
        relativeTime: review.relative_time_description,
        language: review.language,
      })) || [],
      
      editorialSummary: place.editorial_summary?.overview,
      
      raw: place,
    };
  }

  /**
   * Format raw Places API results into cleaner structure
   * @param {Array} results - Raw results from Places API
   * @returns {Array} Formatted results
   */
  formatResults(results) {
    return results.map(place => ({
      placeId: place.place_id,
      name: place.name,
      address: place.vicinity || place.formatted_address,
      location: place.geometry.location,
      rating: place.rating,
      ratingsCount: place.user_ratings_total,
      priceLevel: place.price_level,
      isOpen: place.opening_hours?.open_now,
      types: place.types,
      photoReference: place.photos?.[0]?.photo_reference,
    }));
  }

  /**
   * Get photo URL for a place
   * @param {string} photoReference - Photo reference from Places API
   * @param {number} maxWidth - Maximum width of the photo
   * @returns {string} Photo URL
   */
  getPhotoUrl(photoReference, maxWidth = 400) {
    return `https://maps.googleapis.com/maps/api/place/photo?maxwidth=${maxWidth}&photoreference=${photoReference}&key=${this.apiKey}`;
  }
}

module.exports = PlacesService;

