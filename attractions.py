from flask import Blueprint, request, jsonify
from models import EnhancedAttraction
from bson import ObjectId
import json

attractions_bp = Blueprint('attractions', __name__)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def convert_objectids(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(v) for v in obj]
    else:
        return obj


@attractions_bp.route('/attractions', methods=['GET'])
def get_attractions():
    try:
        region = request.args.get('region')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 20))

        if region:
            attractions = EnhancedAttraction.find_by_region(region)
        elif category:
            attractions = EnhancedAttraction.find_by_category(category)
        else:
            attractions = list(EnhancedAttraction.get_collection().find().limit(limit))

        attractions = convert_objectids(attractions)

        return jsonify({
            'success': True,
            'count': len(attractions),
            'attractions': attractions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@attractions_bp.route('/attractions/search', methods=['GET'])
def search_attractions():
    try:
        query = request.args.get('q', '')
        region = request.args.get('region')

        search_filter = {}
        if query:
            search_filter['name'] = {'$regex': query, '$options': 'i'}
        if region:
            search_filter['region'] = region

        attractions = list(EnhancedAttraction.get_collection().find(search_filter).limit(15))
        attractions = convert_objectids(attractions)

        return jsonify({
            'success': True,
            'count': len(attractions),
            'attractions': attractions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@attractions_bp.route('/attractions/<attraction_id>', methods=['GET'])
def get_attraction_detail(attraction_id):
    try:
        attraction = EnhancedAttraction.get_collection().find_one({'_id': ObjectId(attraction_id)})

        if not attraction:
            return jsonify({
                'success': False,
                'error': 'Attraction not found'
            }), 404

        attraction = convert_objectids(attraction)

        return jsonify({
            'success': True,
            'attraction': attraction
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@attractions_bp.route('/attractions/regions/<region>', methods=['GET'])
def get_attractions_by_region(region):
    try:
        attractions = EnhancedAttraction.find_by_region(region)
        attractions = convert_objectids(attractions)

        return jsonify({
            'success': True,
            'count': len(attractions),
            'region': region,
            'attractions': attractions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attractions_bp.route('/attractions/<attraction_id>/full', methods=['GET'])
def get_attraction_full_details(attraction_id):
    try:
        attraction = EnhancedAttraction.get_collection().find_one({'_id': ObjectId(attraction_id)})

        if not attraction:
            return jsonify({
                'success': False,
                'error': 'Attraction not found'
            }), 404

        attraction = convert_objectids(attraction)

        from models import EnhancedHotel
        nearby_hotels = EnhancedHotel.find_by_city(attraction.get('city'), limit=5)
        nearby_hotels = convert_objectids(nearby_hotels)
        similar_attractions = list(EnhancedAttraction.get_collection().find({
            'region': attraction.get('region'),
            'category': attraction.get('category'),
            '_id': {'$ne': ObjectId(attraction_id)}
        }).limit(4))
        similar_attractions = convert_objectids(similar_attractions)
        city_attractions = list(EnhancedAttraction.get_collection().find({
            'city': attraction.get('city'),
            '_id': {'$ne': ObjectId(attraction_id)}
        }).limit(3))
        city_attractions = convert_objectids(city_attractions)

        detailed_info = {
            'description': attraction.get('description', 'No description available'),
            'detailed_description': attraction.get('detailed_description', attraction.get('description',
                                                                                          'Explore this beautiful destination.')),
            'best_season': attraction.get('best_season', ['All year']),
            'best_time_to_visit': attraction.get('best_time_to_visit', 'Throughout the year'),
            'opening_hours': attraction.get('opening_hours', 'Sunrise to Sunset'),
            'visit_duration': attraction.get('visit_duration', '2-3 hours'),
            'difficulty_level': attraction.get('difficulty_level', 'Easy'),
            'entrance_fee': attraction.get('entrance_fee', 0),
            'nearby_facilities': attraction.get('nearby_facilities', []),
            'activities': attraction.get('activities', []),
            'essential_tips': attraction.get('essential_tips', [
                'Carry water and snacks',
                'Wear comfortable shoes',
                'Check weather before visiting'
            ]),
            'things_to_carry': attraction.get('things_to_carry', [
                'Water bottle',
                'Camera',
                'Sunscreen',
                'Comfortable footwear'
            ]),
            'parking_available': attraction.get('parking_available', True),
            'wheelchair_accessible': attraction.get('wheelchair_accessible', False),
            'family_friendly': attraction.get('family_friendly', True),
            'safety_rating': attraction.get('safety_rating', 4),
            'local_transport': attraction.get('local_transport', 'Available via taxi or local transport'),
            'coordinates': attraction.get('location', {}).get('coordinates') if attraction.get('location') else None
        }

        return jsonify({
            'success': True,
            'attraction': {
                '_id': attraction['_id'],
                'name': attraction.get('name', ''),
                'image_url': attraction.get('image_url'),
                'region': attraction.get('region'),
                'city': attraction.get('city'),
                'category': attraction.get('category'),
                'detailed_info': detailed_info
            },
            'nearby_hotels': nearby_hotels,
            'similar_attractions': similar_attractions,
            'city_attractions': city_attractions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500