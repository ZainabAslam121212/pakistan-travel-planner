from flask import Blueprint, request, jsonify
from models import EnhancedHotel
from bson import ObjectId
from models import EnhancedAttraction

hotels_bp = Blueprint('hotels', __name__)


def convert_objectids(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(v) for v in obj]
    else:
        return obj


@hotels_bp.route('/hotels', methods=['GET'])
def get_hotels():
    try:
        region = request.args.get('region')
        budget = request.args.get('budget')
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        limit = int(request.args.get('limit', 10))

        if lat and lng:
            hotels = EnhancedHotel.find_nearby(lat, lng, limit=limit)
        elif region and budget:
            hotels = EnhancedHotel.find_by_budget(region, budget, limit=limit)
        elif region:
            hotels = list(EnhancedHotel.get_collection().find({'region': region}).limit(limit))
        else:
            hotels = list(EnhancedHotel.get_collection().find().limit(limit))

        hotels = convert_objectids(hotels)

        return jsonify({
            'success': True,
            'count': len(hotels),
            'hotels': hotels
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hotels_bp.route('/hotels/near-attraction', methods=['GET'])
def get_hotels_near_attraction():
    try:
        attraction_id = request.args.get('attraction_id')
        max_distance = int(request.args.get('max_distance', 50000))
        budget = request.args.get('budget', 'medium')

        if not attraction_id:
            return jsonify({
                'success': False,
                'error': 'attraction_id is required'
            }), 400



        attraction = EnhancedAttraction.get_collection().find_one({'_id': ObjectId(attraction_id)})

        if not attraction:
            return jsonify({
                'success': False,
                'error': 'Attraction not found'
            }), 404

        location = attraction['location']['coordinates']
        lat, lng = location[1], location[0]

        hotels = EnhancedHotel.find_nearby(lat, lng, max_distance, limit=5)

        if budget:
            budget_map = {
                'low': (1000, 5000),
                'medium': (5000, 15000),
                'high': (15000, 50000)
            }
            min_price, max_price = budget_map.get(budget, (1000, 15000))
            hotels = [h for h in hotels if min_price <= h.get('price_per_night', 0) <= max_price]

        hotels = convert_objectids(hotels)

        return jsonify({
            'success': True,
            'count': len(hotels),
            'hotels': hotels
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hotels_bp.route('/hotels/<hotel_id>', methods=['GET'])
def get_hotel_detail(hotel_id):
    try:
        hotel = EnhancedHotel.get_collection().find_one({'_id': ObjectId(hotel_id)})

        if not hotel:
            return jsonify({
                'success': False,
                'error': 'Hotel not found'
            }), 404

        hotel = convert_objectids(hotel)

        return jsonify({
            'success': True,
            'hotel': hotel
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500