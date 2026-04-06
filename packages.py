from flask import Blueprint, request, jsonify
from models import EnhancedAttraction, EnhancedHotel
from models import EnhancedPackage
from bson import ObjectId


class AdvancedRecommendationEngine:
    def __init__(self):
        self.region_attractions = {
            'northern': ['Fairy Meadows', 'Nanga Parbat Base Camp', 'Attabad Lake', 'Passu Cones',
                         'Deosai Plains', 'Shangrila Resort', 'Upper Hunza', 'Rakaposhi Viewpoint'],
            'punjab': ['Badshahi Mosque', 'Lahore Fort', 'Shalimar Gardens', 'Wagah Border',
                       'Katas Raj Temples', 'Rohtas Fort', 'Taxila Museum', 'Hiran Minar'],
            'sindh': ['Mohenjo-daro', 'Makkli Necropolis', 'Kehnjar Lake', 'Chaukhandi Tombs',
                      'Shah Jahan Mosque', 'Kot Diji Fort', 'Ranikot Fort', 'Gorakh Hill'],
            'balochistan': ['Makkran Coast', 'Hingol National Park', 'Princess of Hope',
                            'Kund Malir Beach', 'Gwadar Port', 'Hanna Lake', 'Quaid-e-Azam Residency'],
            'kpk': ['Kumrat Valley', 'Swat Valley', 'Khyber Pass', 'Takht-i-Bahi',
                    'Mahodand Lake', 'Saif-ul-Mulook Lake', 'Ayubia National Park']
        }

        self.category_activities = {
            'adventure': ['Hiking', 'Trekking', 'Rock Climbing', 'River Rafting', 'Camping',
                          'Paragliding', 'Mountain Biking', 'Jeep Safari'],
            'cultural': ['Local Food Tasting', 'Traditional Craft Workshop', 'Cultural Performance',
                         'Village Homestay', 'Local Market Exploration', 'Festival Participation'],
            'historical': ['Guided Fort Tour', 'Museum Visit', 'Archaeological Site Exploration',
                           'Historical Walk', 'Heritage Building Photography']
        }

    def get_top_attractions(self, user_preferences):
        # Get region-specific attractions
        attractions = EnhancedAttraction.find_by_preferences(user_preferences, limit=5)

        return attractions

    def generate_activities(self, attractions, user_preferences):
        category = user_preferences.get('category', 'adventure')
        base_activities = []

        for attraction in attractions:
            activity = {
                'name': f"Explore {attraction['name']}",
                'duration': f"{attraction.get('time_required', 2)} hours",
                'type': 'sightseeing',
                'description': f"Visit {attraction['name']} - {attraction.get('description', 'Popular attraction')}"
            }
            base_activities.append(activity)

        # Add category-specific activities
        category_activities = self.category_activities.get(category, [])
        for activity_name in category_activities[:2]:
            base_activities.append({
                'name': activity_name,
                'duration': '2-3 hours',
                'type': category,
                'description': f"{category.capitalize()} activity in the region"
            })

        return base_activities

    def suggest_transportation(self, user_preferences):
        group_type = user_preferences.get('group_type', 'couple')
        region = user_preferences.get('region', 'northern')

        transportation = {
            'solo': {'type': 'car_rental', 'vehicle': 'Hatchback', 'cost_per_day': 3000},
            'couple': {'type': 'car_rental', 'vehicle': 'Sedan', 'cost_per_day': 4000},
            'family': {'type': 'van_rental', 'vehicle': '7-seater Van', 'cost_per_day': 6000},
            'friends': {'type': 'car_rental', 'vehicle': 'SUV', 'cost_per_day': 5000}
        }

        base_transport = transportation.get(group_type, transportation['couple'])

        # Adjust for region
        if region == 'northern':
            base_transport['vehicle'] = '4x4 Jeep'
            base_transport['cost_per_day'] += 1000

        return base_transport

    def suggest_food(self, region):
        regional_foods = {
            'northern': ['Chapshuro', 'Hunza Bread', 'Butter Tea', 'Apricot Soup', 'Local Trout'],
            'punjab': ['Nihari', 'Haleem', 'Paye', 'Karahi', 'Lassi', 'Siri Paye'],
            'sindh': ['Sindhi Biryani', 'Pallo Fish', 'Saag', 'Kadi Chawal', 'Seyal Mani'],
            'balochistan': ['Sajji', 'Kaak', 'Dampukht', 'Landhi', 'Khaddi Kebab'],
            'kpk': ['Chapli Kebab', 'Shinwari Karahi', 'Peshawari Ice Cream', 'Kabuli Pulao']
        }

        return regional_foods.get(region, ['Local Cuisine', 'Traditional Food'])

class AdvancedPackageGenerator:
    def __init__(self):
        self.recommendation_engine = AdvancedRecommendationEngine()

    def generate_custom_package(self, user_preferences):
        # Get top attractions based on preferences
        top_attractions = self.recommendation_engine.get_top_attractions(user_preferences)

        # Get nearby hotels
        region = user_preferences.get('region', 'northern')
        budget = user_preferences.get('budget_range', 'medium')
        nearby_hotels = EnhancedHotel.find_by_budget(region, budget)

        # Calculate package details
        duration = int(user_preferences.get('duration', 5))
        total_cost = self.calculate_total_cost(top_attractions, nearby_hotels, duration, user_preferences)

        # Generate activities
        activities = self.recommendation_engine.generate_activities(top_attractions, user_preferences)

        # Get transportation suggestions
        transportation = self.recommendation_engine.suggest_transportation(user_preferences)

        # Get food suggestions
        food_suggestions = self.recommendation_engine.suggest_food(region)

        custom_package = {
            'name': f"Custom {user_preferences.get('category', 'Adventure')} Tour - {region.capitalize()}",
            'type': 'custom',
            'category': user_preferences.get('category', 'adventure'),
            'region': region,
            'duration_days': duration,
            'price': total_cost,
            'description': self.generate_package_description(user_preferences, top_attractions),
            'attractions': top_attractions,
            'hotels': nearby_hotels,
            'activities': activities,
            'transportation': transportation,
            'food_suggestions': food_suggestions,
            'itinerary': self.generate_detailed_itinerary(top_attractions, duration)
        }

        return custom_package

    def calculate_total_cost(self, attractions, hotels, duration, user_preferences):
        # Calculate attraction costs
        attraction_cost = sum(attraction.get('entry_fee', 0) for attraction in attractions)

        # Calculate hotel costs
        hotel_cost = 0
        if hotels:
            avg_hotel_price = sum(hotel.get('price_per_night', 3000) for hotel in hotels) / len(hotels)
            hotel_cost = avg_hotel_price * duration

        # Transportation cost
        transportation = self.recommendation_engine.suggest_transportation(user_preferences)
        transport_cost = transportation.get('cost_per_day', 4000) * duration

        # Food cost (estimated)
        food_cost = 2000 * duration * 3  # 3 meals per day

        # Guide and miscellaneous costs
        guide_cost = 1500 * duration
        misc_cost = 1000 * duration

        total_cost = attraction_cost + hotel_cost + transport_cost + food_cost + guide_cost + misc_cost

        # Apply budget adjustments
        budget = user_preferences.get('budget_range', 'medium')
        if budget == 'low':
            total_cost *= 0.8
        elif budget == 'high':
            total_cost *= 1.3

        return round(total_cost)

    def generate_package_description(self, user_preferences, attractions):
        region = user_preferences.get('region', 'northern').capitalize()
        category = user_preferences.get('category', 'adventure').capitalize()
        duration = user_preferences.get('duration', 5)

        attraction_names = [attr['name'] for attr in attractions[:3]]

        return f"{duration}-day {category} tour exploring {region} region. Visit {', '.join(attraction_names)} and experience the best of Pakistani tourism with comfortable accommodation and guided activities."

    def generate_detailed_itinerary(self, attractions, duration):
        itinerary = []

        for day in range(1, duration + 1):
            if day == 1:
                itinerary.append({
                    'day': day,
                    'title': 'Arrival and Orientation',
                    'activities': [
                        'Arrive at destination',
                        'Hotel check-in',
                        'Briefing session with guide',
                        'Local market visit for dinner'
                    ]
                })
            elif day == duration:
                itinerary.append({
                    'day': day,
                    'title': 'Departure',
                    'activities': [
                        'Breakfast at hotel',
                        'Last-minute souvenir shopping',
                        'Check-out from hotel',
                        'Departure transfer'
                    ]
                })
            else:
                # Distribute attractions across days
                attraction_index = (day - 2) % len(attractions) if attractions else 0
                attraction = attractions[attraction_index] if attractions else {}

                itinerary.append({
                    'day': day,
                    'title': f"Explore {attraction.get('name', 'Local Attractions')}",
                    'activities': [
                        f"Breakfast at hotel",
                        f"Visit {attraction.get('name', 'local attraction')}",
                        "Lunch at local restaurant",
                        "Evening cultural activity",
                        "Dinner and overnight stay"
                    ]
                })

        return itinerary


packages_bp = Blueprint('packages', __name__)
package_generator = AdvancedPackageGenerator()


def convert_objectids(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(v) for v in obj]
    else:
        return obj


# Pre-made Packages
@packages_bp.route('/packages', methods=['GET'])
def get_packages():
    try:
        filters = {
            'region': request.args.get('region'),
            'category': request.args.get('category'),
            'max_budget': request.args.get('max_budget'),
            'min_nights': request.args.get('min_nights')
        }

        filters = {k: v for k, v in filters.items() if v is not None}

        packages = EnhancedPackage.find_by_filters(filters)
        packages = convert_objectids(packages)

        return jsonify({
            'success': True,
            'count': len(packages),
            'packages': packages
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Custom Package Generation
@packages_bp.route('/packages/custom', methods=['POST'])
def create_custom_package():
    try:
        data = request.get_json()
        user_preferences = data.get('preferences', {})

        if not user_preferences:
            return jsonify({
                'success': False,
                'error': 'Preferences are required'
            }), 400

        # Validate required fields
        required_fields = ['region', 'category', 'duration', 'budget_range']
        for field in required_fields:
            if field not in user_preferences:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        custom_package = package_generator.generate_custom_package(user_preferences)
        custom_package = convert_objectids(custom_package)

        return jsonify({
            'success': True,
            'package': custom_package
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Metadata endpoints
@packages_bp.route('/metadata/regions', methods=['GET'])
def get_regions():
    regions = [
        {'id': 'northern', 'name': 'Northern Areas', 'description': 'Gilgit-Baltistan and surrounding mountain regions',
         'image': 'northern_areas.jpg'},
        {'id': 'punjab', 'name': 'Punjab', 'description': 'Cultural heartland with historical sites and vibrant cities',
         'image': 'punjab.jpg'},
        {'id': 'sindh', 'name': 'Sindh', 'description': 'Historical and coastal regions with ancient civilizations',
         'image': 'sindh.jpg'},
        {'id': 'balochistan', 'name': 'Balochistan',
         'description': 'Desert landscapes and coastal beauty along Makran Coast', 'image': 'balochistan.jpg'},
        {'id': 'kpk', 'name': 'Khyber Pakhtunkhwa', 'description': 'Mountains, valleys and rich cultural heritage',
         'image': 'kpk.jpg'}
    ]
    return jsonify(regions)


@packages_bp.route('/metadata/categories', methods=['GET'])
def get_categories():
    categories = [
        {'id': 'adventure', 'name': 'Adventure', 'description': 'Hiking, trekking, and outdoor activities',
         'icon': '🧗'},
        {'id': 'cultural', 'name': 'Cultural', 'description': 'Heritage, museums, and cultural experiences',
         'icon': '🎭'},
        {'id': 'historical', 'name': 'Historical', 'description': 'Forts, mosques, and historical sites', 'icon': '🏛️'},
        {'id': 'religious', 'name': 'Religious', 'description': 'Religious sites and spiritual journeys', 'icon': '🕌'},
        {'id': 'beach', 'name': 'Beach & Relaxation', 'description': 'Coastal areas and relaxation', 'icon': '🏖️'}
    ]
    return jsonify(categories)


@packages_bp.route('/packages/<package_id>', methods=['GET'])
def get_package_detail(package_id):
    try:
        package = EnhancedPackage.get_collection().find_one({'_id': ObjectId(package_id)})

        if not package:
            return jsonify({
                'success': False,
                'error': 'Package not found'
            }), 404

        package = convert_objectids(package)

        return jsonify({
            'success': True,
            'package': package
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@packages_bp.route('/metadata/budget-ranges', methods=['GET'])
def get_budget_ranges():
    budget_ranges = [
        {'id': 'low', 'name': 'Budget (Under PKR 20,000)', 'range': 'PKR 5,000 - 20,000'},
        {'id': 'medium', 'name': 'Standard (PKR 20,000 - 50,000)', 'range': 'PKR 20,000 - 50,000'},
        {'id': 'high', 'name': 'Luxury (PKR 50,000+)', 'range': 'PKR 50,000 - 150,000+'}
    ]
    return jsonify(budget_ranges)


@packages_bp.route('/metadata/durations', methods=['GET'])
def get_durations():
    durations = [
        {'id': '3', 'name': 'Weekend Getaway (3 days)', 'description': 'Short trip perfect for weekends'},
        {'id': '5', 'name': 'Extended Weekend (5 days)', 'description': 'Perfect for long weekends'},
        {'id': '7', 'name': 'Week Long (7 days)', 'description': 'Comprehensive week-long exploration'},
        {'id': '10', 'name': 'In-depth (10 days)', 'description': 'Thorough exploration of the region'},
        {'id': '14', 'name': 'Extended Tour (14 days)', 'description': 'Complete immersive experience'}
    ]
    return jsonify(durations)
