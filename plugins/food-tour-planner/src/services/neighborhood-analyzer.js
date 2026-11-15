const { Client } = require('@googlemaps/google-maps-services-js');

class NeighborhoodAnalyzer {
  constructor(apiKey) {
    this.client = new Client({});
    this.apiKey = apiKey;
  }

  /**
   * Analyze entire neighborhood using multiple overlapping search points
   * @param {Array<{lat: number, lng: number, name?: string}>} searchPoints - Grid of coordinates covering area
   * @param {Object} options
   * @param {number} options.radius - Radius per search point (default 200)
   * @param {Array<string>} options.types - Place types to search
   * @returns {Promise<Array>} Deduplicated list of all establishments
   */
  async analyzeNeighborhood(searchPoints, options = {}) {
    const {
      radius = 200,
      types = ['restaurant', 'cafe', 'bar', 'bakery', 'meal_takeaway'],
    } = options;

    console.log(`\nAnalyzing neighborhood with ${searchPoints.length} search points`);
    console.log(`Radius per point: ${radius}m`);
    console.log('='.repeat(70));

    const allPlaces = new Map(); // Map by place_id to automatically deduplicate
    let totalResults = 0;

    for (let i = 0; i < searchPoints.length; i++) {
      const point = searchPoints[i];
      console.log(`\n[${i + 1}/${searchPoints.length}] Searching near ${point.name || `(${point.lat}, ${point.lng})`}...`);

      for (const type of types) {
        try {
          const response = await this.client.placesNearby({
            params: {
              location: { lat: point.lat, lng: point.lng },
              radius: radius,
              type: type,
              key: this.apiKey,
            },
          });

          const newResults = response.data.results.length;
          totalResults += newResults;

          response.data.results.forEach(place => {
            // Using Map with place_id as key automatically deduplicates
            allPlaces.set(place.place_id, place);
          });

          await this.sleep(100); // Rate limiting

        } catch (error) {
          console.log(`   ✗ Error searching ${type}: ${error.message}`);
        }
      }

      const duplicates = totalResults - allPlaces.size;
      console.log(`   ✓ Total unique places: ${allPlaces.size} (${duplicates} duplicates removed)`);
    }

    console.log('\n' + '='.repeat(70));
    console.log(`✓ Found ${allPlaces.size} unique establishments`);
    console.log(`✓ Removed ${totalResults - allPlaces.size} duplicates automatically`);

    return Array.from(allPlaces.values());
  }

  /**
   * Get comprehensive data for all places in neighborhood
   * @param {Array} places - Array of places from analyzeNeighborhood
   * @returns {Promise<Array>} Detailed establishment data
   */
  async getDetailedData(places) {
    console.log('\n[Step 2] Collecting detailed data for each establishment...');
    console.log('='.repeat(70));

    const establishments = [];

    for (let i = 0; i < places.length; i++) {
      const place = places[i];
      console.log(`\n[${i + 1}/${places.length}] ${place.name}...`);

      try {
        const details = await this.client.placeDetails({
          params: {
            place_id: place.place_id,
            fields: [
              'place_id',
              'name',
              'formatted_address',
              'geometry',
              'rating',
              'user_ratings_total',
              'price_level',
              'types',
              'opening_hours',
              'photos',
              'website',
              'formatted_phone_number',
              'reviews',
              'editorial_summary',
              'url',
              'delivery',
              'dine_in',
              'takeout',
              'reservable',
              'serves_breakfast',
              'serves_lunch',
              'serves_dinner',
              'serves_brunch',
              'serves_vegetarian_food',
            ],
            key: this.apiKey,
          },
        });

        const d = details.data.result;

        establishments.push({
          name: d.name,
          placeId: d.place_id,
          googleMapsUrl: d.url,
          address: d.formatted_address,
          coordinates: {
            lat: d.geometry?.location?.lat,
            lng: d.geometry?.location?.lng,
          },
          rating: d.rating || null,
          totalReviews: d.user_ratings_total || 0,
          priceLevel: d.price_level ? '$'.repeat(d.price_level) : null,
          categories: d.types?.filter(t => 
            !['establishment', 'point_of_interest'].includes(t)
          ) || [],
          editorial: d.editorial_summary?.overview || null,
          website: d.website || null,
          phone: d.formatted_phone_number || null,
          hours: {
            currentlyOpen: d.opening_hours?.open_now || false,
            schedule: d.opening_hours?.weekday_text || [],
          },
          services: {
            dineIn: d.dine_in === true,
            takeout: d.takeout === true,
            delivery: d.delivery === true,
            reservations: d.reservable === true,
          },
          meals: {
            breakfast: d.serves_breakfast === true,
            brunch: d.serves_brunch === true,
            lunch: d.serves_lunch === true,
            dinner: d.serves_dinner === true,
          },
          dietary: {
            vegetarian: d.serves_vegetarian_food === true,
          },
          photos: (d.photos || []).slice(0, 10).map(photo => ({
            url: `https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference=${photo.photo_reference}&key=${this.apiKey}`,
            width: photo.width,
            height: photo.height,
          })),
          reviews: (d.reviews || []).map(review => ({
            author: review.author_name,
            rating: review.rating,
            text: review.text,
            publishedTime: review.time,
            relativeTime: review.relative_time_description,
          })),
        });

        console.log(`   ✓ ${d.rating || 'N/A'}★ | ${d.user_ratings_total || 0} reviews`);
        await this.sleep(200);

      } catch (error) {
        console.log(`   ✗ Error: ${error.message}`);
      }
    }

    console.log('\n' + '='.repeat(70));
    console.log(`✓ Collected data for ${establishments.length} establishments`);

    return establishments;
  }

  /**
   * Generate grid of search points to cover an area
   * @param {Object} bounds - Bounding box {north, south, east, west}
   * @param {number} spacing - Distance between points in meters (default 300)
   * @returns {Array} Grid of coordinate points
   */
  generateSearchGrid(bounds, spacing = 300) {
    const points = [];
    
    // Convert spacing from meters to approximate degrees
    // 1 degree latitude ≈ 111km
    // 1 degree longitude ≈ 111km * cos(latitude)
    const latSpacing = spacing / 111000;
    const lngSpacing = spacing / (111000 * Math.cos(bounds.center.lat * Math.PI / 180));

    let lat = bounds.south;
    let gridRow = 0;

    while (lat <= bounds.north) {
      let lng = bounds.west;
      let gridCol = 0;

      while (lng <= bounds.east) {
        points.push({
          lat: lat,
          lng: lng,
          name: `Grid[${gridRow},${gridCol}]`,
        });
        lng += lngSpacing;
        gridCol++;
      }

      lat += latSpacing;
      gridRow++;
    }

    return points;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = NeighborhoodAnalyzer;

