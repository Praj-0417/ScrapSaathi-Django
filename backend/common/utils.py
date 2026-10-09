"""
Utility functions: Standard API response envelopes, Geocoding index, and Serviceability math.
"""

import math
from rest_framework.response import Response
from common.constants import SERVICE_HUBS

INDIAN_LOCALITIES = [
    {'name': 'Connaught Place, Central Delhi', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.6315, 'lon': 77.2167, 'keywords': ['connaught', 'cp', 'delhi', 'central delhi']},
    {'name': 'Hauz Khas, South Delhi', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.5494, 'lon': 77.2001, 'keywords': ['hauz khas', 'south delhi', 'iit delhi']},
    {'name': 'Dwarka Sector 10, South West Delhi', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.5823, 'lon': 77.0500, 'keywords': ['dwarka', 'south west delhi', 'sector 10']},
    {'name': 'Lajpat Nagar Central Market', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.5677, 'lon': 77.2433, 'keywords': ['lajpat', 'lajpat nagar', 'south delhi']},
    {'name': 'Karol Bagh Market', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.6517, 'lon': 77.1906, 'keywords': ['karol bagh', 'west delhi']},
    {'name': 'Rohini Sector 7, North West Delhi', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.7166, 'lon': 77.1126, 'keywords': ['rohini', 'north west delhi']},
    {'name': 'Saket District Centre, South Delhi', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.5244, 'lon': 77.2185, 'keywords': ['saket', 'select citywalk', 'south delhi']},
    {'name': 'Sector 62, Noida', 'city': 'Noida', 'state': 'Uttar Pradesh', 'lat': 28.6270, 'lon': 77.3725, 'keywords': ['noida 62', 'sector 62', 'noida', 'electronic city']},
    {'name': 'Sector 18, Noida Atta Market', 'city': 'Noida', 'state': 'Uttar Pradesh', 'lat': 28.5708, 'lon': 77.3260, 'keywords': ['sector 18', 'atta market', 'noida', 'dlf mall']},
    {'name': 'DLF Cyber City, Phase 2, Gurugram', 'city': 'Gurugram', 'state': 'Haryana', 'lat': 28.4950, 'lon': 77.0895, 'keywords': ['cyber city', 'gurgaon', 'gurugram', 'dlf']},
    {'name': 'Golf Course Road, Sector 54, Gurugram', 'city': 'Gurugram', 'state': 'Haryana', 'lat': 28.4357, 'lon': 77.1054, 'keywords': ['golf course road', 'sector 54', 'gurgaon']},
    {'name': 'Indirapuram, Ghaziabad', 'city': 'Ghaziabad', 'state': 'Uttar Pradesh', 'lat': 28.6415, 'lon': 77.3714, 'keywords': ['indirapuram', 'ghaziabad', 'vaishali']},
    {'name': 'Greater Noida West (Noida Extension)', 'city': 'Greater Noida', 'state': 'Uttar Pradesh', 'lat': 28.6090, 'lon': 77.4363, 'keywords': ['greater noida', 'noida extension', 'gaur city']},

    # Mumbai & MMR
    {'name': 'Bandra West, Hill Road, Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.0596, 'lon': 72.8295, 'keywords': ['bandra', 'bandra west', 'mumbai', 'linking road']},
    {'name': 'Andheri East, MIDC & Chakala, Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.1136, 'lon': 72.8697, 'keywords': ['andheri', 'andheri east', 'chakala', 'midc']},
    {'name': 'Andheri West, Lokhandwala Complex, Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.1363, 'lon': 72.8277, 'keywords': ['andheri west', 'lokhandwala', 'mumbai']},
    {'name': 'Powai, Hiranandani Gardens, Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.1197, 'lon': 72.9051, 'keywords': ['powai', 'hiranandani', 'iit bombay', 'mumbai']},
    {'name': 'Juhu Tara Road & Beach, Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.0988, 'lon': 72.8264, 'keywords': ['juhu', 'juhu beach', 'mumbai']},
    {'name': 'Dadar West, Shivaji Park, Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.0269, 'lon': 72.8374, 'keywords': ['dadar', 'shivaji park', 'mumbai']},
    {'name': 'Colaba Causeway & Fort, South Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 18.9067, 'lon': 72.8147, 'keywords': ['colaba', 'fort', 'gateway of india', 'south mumbai']},
    {'name': 'Borivali West, IC Colony, Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.2307, 'lon': 72.8567, 'keywords': ['borivali', 'borivali west', 'ic colony']},
    {'name': 'Thane West, Ghodbunder Road', 'city': 'Thane', 'state': 'Maharashtra', 'lat': 19.2183, 'lon': 72.9781, 'keywords': ['thane', 'ghodbunder road', 'thane west']},
    {'name': 'Vashi Sector 17, Navi Mumbai', 'city': 'Navi Mumbai', 'state': 'Maharashtra', 'lat': 19.0771, 'lon': 72.9986, 'keywords': ['vashi', 'navi mumbai', 'sector 17']},

    # Bengaluru
    {'name': 'Indiranagar 100 Feet Road, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 12.9784, 'lon': 77.6408, 'keywords': ['indiranagar', '100 feet road', 'bengaluru', 'bangalore']},
    {'name': 'Koramangala 5th Block, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 12.9352, 'lon': 77.6245, 'keywords': ['koramangala', '5th block', 'bengaluru', 'sony world']},
    {'name': 'HSR Layout Sector 2, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 12.9121, 'lon': 77.6446, 'keywords': ['hsr', 'hsr layout', 'bengaluru']},
    {'name': 'Whitefield, ITPL Main Road, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 12.9698, 'lon': 77.7500, 'keywords': ['whitefield', 'itpl', 'bengaluru', 'hope farm']},
    {'name': 'Electronic City Phase 1, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 12.8452, 'lon': 77.6602, 'keywords': ['electronic city', 'ecity', 'bengaluru', 'infosys']},
    {'name': 'Jayanagar 4th Block, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 12.9250, 'lon': 77.5938, 'keywords': ['jayanagar', '4th block', 'bengaluru']},
    {'name': 'Malleshwaram, Sampige Road, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 13.0031, 'lon': 77.5701, 'keywords': ['malleshwaram', 'sampige road', 'bengaluru']},
    {'name': 'Marathahalli Bridge, Bengaluru', 'city': 'Bengaluru', 'state': 'Karnataka', 'lat': 12.9591, 'lon': 77.6974, 'keywords': ['marathahalli', 'outer ring road', 'bengaluru']},
]

def api_success(data=None, message='OK', status_code=200, meta=None):
    """Generates standard success envelope matching Express monolith apiResponse.js."""
    return Response(
        {
            'success': True,
            'message': message,
            'data': data,
            'meta': meta or {},
            'errors': [],
        },
        status=status_code,
    )

def api_failure(message='Internal Server Error', status_code=500, errors=None, meta=None):
    """Generates standard failure envelope matching Express monolith apiResponse.js."""
    return Response(
        {
            'success': False,
            'message': message,
            'data': None,
            'meta': meta or {},
            'errors': errors or [],
        },
        status=status_code,
    )

def check_serviceability(lat, lon):
    """
    Checks whether given lat/lon coordinates fall within an active ScrapSaathi service hub.
    Uses spherical Haversine formula.
    """
    if lat is None or lon is None:
        return {'serviceable': False, 'nearestHub': None}

    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        return {'serviceable': False, 'nearestHub': None}

    min_distance = float('inf')
    closest_hub = None

    for hub in SERVICE_HUBS:
        d_lat = math.radians(hub['lat'] - lat)
        d_lon = math.radians(hub['lon'] - lon)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat))
            * math.cos(math.radians(hub['lat']))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = 6371 * c

        if distance_km < min_distance:
            min_distance = distance_km
            closest_hub = hub

        if distance_km <= hub['maxRadiusKm']:
            return {
                'serviceable': True,
                'hub': hub['name'],
                'hubId': hub['id'],
                'distanceKm': round(distance_km, 1),
            }

    return {
        'serviceable': False,
        'nearestHub': closest_hub['name'] if closest_hub else None,
        'distanceKm': round(min_distance, 1),
    }

def find_local_localities(query, limit=5):
    """Matches search terms against indexed Indian localities."""
    q = query.lower().strip()
    if not q:
        return []

    matches = []
    for loc in INDIAN_LOCALITIES:
        if (
            q in loc['name'].lower()
            or q in loc['city'].lower()
            or any(q in k or k in q for k in loc['keywords'])
        ):
            matches.append({
                'display_name': f"{loc['name']}, {loc['city']}, {loc['state']}, India",
                'lat': str(loc['lat']),
                'lon': str(loc['lon']),
                'city': loc['city'],
                'state': loc['state'],
                'country': 'India',
                'source': 'verified_directory',
            })
            if len(matches) >= limit:
                break
    return matches

def reverse_lookup_locality(lat, lon):
    """Finds nearest locality from directory or produces coordinates fallback."""
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        return None

    min_dist = float('inf')
    closest = None

    for loc in INDIAN_LOCALITIES:
        dist = math.sqrt((loc['lat'] - lat) ** 2 + (loc['lon'] - lon) ** 2)
        if dist < min_dist:
            min_dist = dist
            closest = loc

    if closest and min_dist < 0.15:
        addr = f"Near {closest['name']}, {closest['city']}, {closest['state']}"
        return {
            'display_name': addr,
            'formattedAddress': addr,
            'lat': lat,
            'lng': lon,
            'city': closest['city'],
            'state': closest['state'],
        }

    fallback = f"Pickup Location (Lat: {lat:.4f}, Lon: {lon:.4f})"
    return {
        'display_name': fallback,
        'formattedAddress': fallback,
        'lat': lat,
        'lng': lon,
        'city': '',
        'state': '',
    }
