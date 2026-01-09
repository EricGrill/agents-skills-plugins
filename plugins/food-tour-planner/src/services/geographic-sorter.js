class GeographicSorter {
  /**
   * Sort establishments by geographic direction
   * @param {Array} establishments - Array of establishments with coordinates
   * @param {Object} options - Sorting options
   * @returns {Object} Multiple sorted views
   */
  static sortByDirection(establishments, options = {}) {
    const {
      startPoint = null, // Optional starting point for route-based sorting
    } = options;

    return {
      // North to South (highest latitude to lowest)
      northToSouth: [...establishments].sort((a, b) => 
        b.coordinates.lat - a.coordinates.lat
      ),

      // South to North (lowest latitude to highest)
      southToNorth: [...establishments].sort((a, b) => 
        a.coordinates.lat - b.coordinates.lat
      ),

      // West to East (lowest longitude to highest)
      westToEast: [...establishments].sort((a, b) => 
        a.coordinates.lng - b.coordinates.lng
      ),

      // East to West (highest longitude to lowest)
      eastToWest: [...establishments].sort((a, b) => 
        b.coordinates.lng - a.coordinates.lng
      ),

      // Nearest to farthest from start point
      ...(startPoint ? {
        nearestFirst: this.sortByDistance(establishments, startPoint),
      } : {}),

      // Clockwise spiral from center
      clockwiseFromCenter: this.sortClockwise(establishments),

      // Street-by-street grouping
      byStreet: this.groupByStreet(establishments),
    };
  }

  /**
   * Sort by distance from a point
   * @param {Array} establishments
   * @param {Object} startPoint - {lat, lng}
   * @returns {Array} Sorted by nearest first
   */
  static sortByDistance(establishments, startPoint) {
    return [...establishments]
      .map(est => ({
        ...est,
        _distance: this.calculateDistance(
          startPoint.lat,
          startPoint.lng,
          est.coordinates.lat,
          est.coordinates.lng
        ),
      }))
      .sort((a, b) => a._distance - b._distance)
      .map(({ _distance, ...est }) => est);
  }

  /**
   * Sort in clockwise spiral from center
   * Useful for creating circular walking tours
   * @param {Array} establishments
   * @returns {Array} Sorted clockwise
   */
  static sortClockwise(establishments) {
    // Find center point
    const center = this.findCenter(establishments);

    return [...establishments]
      .map(est => ({
        ...est,
        _angle: Math.atan2(
          est.coordinates.lat - center.lat,
          est.coordinates.lng - center.lng
        ),
      }))
      .sort((a, b) => a._angle - b._angle)
      .map(({ _angle, ...est }) => est);
  }

  /**
   * Group establishments by street name
   * @param {Array} establishments
   * @returns {Object} Grouped by street
   */
  static groupByStreet(establishments) {
    const streets = {};

    establishments.forEach(est => {
      const street = this.extractStreetName(est.address);
      if (!streets[street]) {
        streets[street] = [];
      }
      streets[street].push(est);
    });

    // Sort each street north to south
    Object.keys(streets).forEach(street => {
      streets[street].sort((a, b) => 
        b.coordinates.lat - a.coordinates.lat
      );
    });

    return streets;
  }

  /**
   * Create optimal walking route using coordinates
   * @param {Array} establishments
   * @param {Object} startPoint - Starting location {lat, lng}
   * @returns {Array} Optimized route order
   */
  static createWalkingRoute(establishments, startPoint) {
    if (establishments.length === 0) return [];

    const route = [];
    const remaining = [...establishments];
    let current = startPoint;

    // Nearest neighbor algorithm for route optimization
    while (remaining.length > 0) {
      // Find nearest establishment to current position
      let nearestIndex = 0;
      let nearestDistance = this.calculateDistance(
        current.lat,
        current.lng,
        remaining[0].coordinates.lat,
        remaining[0].coordinates.lng
      );

      for (let i = 1; i < remaining.length; i++) {
        const distance = this.calculateDistance(
          current.lat,
          current.lng,
          remaining[i].coordinates.lat,
          remaining[i].coordinates.lng
        );

        if (distance < nearestDistance) {
          nearestDistance = distance;
          nearestIndex = i;
        }
      }

      // Add nearest to route
      const nearest = remaining[nearestIndex];
      route.push({
        ...nearest,
        _walkingDistance: nearestDistance,
        _cumulativeDistance: route.length > 0 
          ? route[route.length - 1]._cumulativeDistance + nearestDistance
          : nearestDistance,
      });

      // Update current position
      current = nearest.coordinates;

      // Remove from remaining
      remaining.splice(nearestIndex, 1);
    }

    return route;
  }

  /**
   * Calculate distance between two points (Haversine formula)
   * @returns {number} Distance in kilometers
   */
  static calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in km
    const dLat = this.toRad(lat2 - lat1);
    const dLng = this.toRad(lng2 - lng1);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRad(lat1)) *
        Math.cos(this.toRad(lat2)) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Find geographic center of establishments
   */
  static findCenter(establishments) {
    const sum = establishments.reduce(
      (acc, est) => ({
        lat: acc.lat + est.coordinates.lat,
        lng: acc.lng + est.coordinates.lng,
      }),
      { lat: 0, lng: 0 }
    );

    return {
      lat: sum.lat / establishments.length,
      lng: sum.lng / establishments.length,
    };
  }

  /**
   * Extract street name from address
   */
  static extractStreetName(address) {
    // Get first part before comma
    const parts = address.split(',');
    if (parts.length === 0) return 'Unknown';

    // Extract street name (remove number)
    const streetPart = parts[0].trim();
    const match = streetPart.match(/[A-Za-z\s]+/);
    return match ? match[0].trim() : 'Unknown';
  }

  /**
   * Convert degrees to radians
   */
  static toRad(degrees) {
    return (degrees * Math.PI) / 180;
  }

  /**
   * Add distance annotations to establishments
   * @param {Array} establishments
   * @param {Object} referencePoint - {lat, lng}
   * @returns {Array} Establishments with distance info
   */
  static annotateDistances(establishments, referencePoint) {
    return establishments.map(est => ({
      ...est,
      distanceFromReference: {
        km: this.calculateDistance(
          referencePoint.lat,
          referencePoint.lng,
          est.coordinates.lat,
          est.coordinates.lng
        ),
        direction: this.getCardinalDirection(
          referencePoint.lat,
          referencePoint.lng,
          est.coordinates.lat,
          est.coordinates.lng
        ),
      },
    }));
  }

  /**
   * Get cardinal direction from point A to point B
   * @returns {string} Direction like "North", "Northeast", etc.
   */
  static getCardinalDirection(lat1, lng1, lat2, lng2) {
    const dLat = lat2 - lat1;
    const dLng = lng2 - lng1;
    const angle = Math.atan2(dLng, dLat) * (180 / Math.PI);

    const directions = [
      'North', 'Northeast', 'East', 'Southeast',
      'South', 'Southwest', 'West', 'Northwest'
    ];

    const index = Math.round(((angle + 360) % 360) / 45) % 8;
    return directions[index];
  }

  /**
   * Generate route summary statistics
   */
  static getRouteSummary(route) {
    if (route.length === 0) return null;

    const totalDistance = route[route.length - 1]._cumulativeDistance;
    const avgDistance = totalDistance / (route.length - 1);

    return {
      totalStops: route.length,
      totalDistance: totalDistance.toFixed(2) + ' km',
      avgDistanceBetweenStops: avgDistance.toFixed(3) + ' km',
      estimatedWalkingTime: Math.ceil(totalDistance / 5 * 60) + ' minutes', // 5 km/h walking speed
      route: route.map((est, idx) => ({
        stop: idx + 1,
        name: est.name,
        rating: est.rating,
        address: est.address,
        walkingDistance: est._walkingDistance ? `${(est._walkingDistance * 1000).toFixed(0)}m` : 'Start',
      })),
    };
  }
}

module.exports = GeographicSorter;


