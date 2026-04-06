from models import EnhancedAttraction

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
        region = user_preferences.get('region', 'northern')
        category = user_preferences.get('category', 'adventure')

        # Get region-specific attractions
        attractions = EnhancedAttraction.find_by_preferences(user_preferences, limit=5)

        # If not enough attractions, add some from our database
        if len(attractions) < 3:
            additional_attractions = self._get_fallback_attractions(region, category)
            attractions.extend(additional_attractions[:5 - len(attractions)])

        return attractions

    def _get_fallback_attractions(self, region, category):
        # Fallback data with real Pakistani attractions
        fallback_data = {
            'northern': [
                {
                    'name': 'Fairy Meadows',
                    'description': 'Beautiful grassland with stunning views of Nanga Parbat',
                    'category': 'hiking',
                    'region': 'northern',
                    'location': {'type': 'Point', 'coordinates': [74.3890, 35.4210]},
                    'entry_fee': 500,
                    'time_required': 6,
                    'best_season': ['spring', 'summer'],
                    'suitable_for': ['solo', 'couple', 'family']
                },
                {
                    'name': 'Attabad Lake',
                    'description': 'Turquoise lake formed after 2010 landslide, famous for boat rides',
                    'category': 'sightseeing',
                    'region': 'northern',
                    'location': {'type': 'Point', 'coordinates': [74.8290, 36.3210]},
                    'entry_fee': 300,
                    'time_required': 4,
                    'best_season': ['spring', 'summer', 'autumn'],
                    'suitable_for': ['solo', 'couple', 'family']
                }
            ],
            'punjab': [
                {
                    'name': 'Badshahi Mosque',
                    'description': 'One of the largest mosques in the world, built by Emperor Aurangzeb',
                    'category': 'historical',
                    'region': 'punjab',
                    'location': {'type': 'Point', 'coordinates': [74.3093, 31.5879]},
                    'entry_fee': 200,
                    'time_required': 2,
                    'best_season': ['winter', 'spring'],
                    'suitable_for': ['solo', 'couple', 'family']
                },
                {
                    'name': 'Lahore Fort',
                    'description': 'Historical fort complex with Mughal architecture',
                    'category': 'fort',
                    'region': 'punjab',
                    'location': {'type': 'Point', 'coordinates': [74.3095, 31.5875]},
                    'entry_fee': 300,
                    'time_required': 3,
                    'best_season': ['winter', 'spring'],
                    'suitable_for': ['solo', 'couple', 'family']
                }
            ],
            'sindh': [
                {
                    'name': 'Mohenjo-daro',
                    'description': 'Archaeological site of ancient Indus Valley Civilization',
                    'category': 'archaeological',
                    'region': 'sindh',
                    'location': {'type': 'Point', 'coordinates': [68.1389, 27.3290]},
                    'entry_fee': 400,
                    'time_required': 4,
                    'best_season': ['winter'],
                    'suitable_for': ['solo', 'couple', 'family']
                }
            ],
            'kpk': [
                {
                    'name': 'Kumrat Valley',
                    'description': 'Beautiful valley with lush green meadows and forests',
                    'category': 'hiking',
                    'region': 'kpk',
                    'location': {'type': 'Point', 'coordinates': [72.1890, 35.2210]},
                    'entry_fee': 0,
                    'time_required': 5,
                    'best_season': ['spring', 'summer'],
                    'suitable_for': ['solo', 'couple', 'family']
                }
            ]
        }

        return fallback_data.get(region, [])

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