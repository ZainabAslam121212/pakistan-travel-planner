from flask_pymongo import PyMongo

mongo = PyMongo()


class EnhancedAttraction:
    @staticmethod
    def get_collection():
        return mongo.db.attractions

    @staticmethod
    def find_by_region(region):
        return list(EnhancedAttraction.get_collection().find({'region': region}))

    @staticmethod
    def find_by_category(category):
        return list(EnhancedAttraction.get_collection().find({'category': category}))

    @staticmethod
    def find_nearby(lat, lng, max_distance=50000, limit=10):
        return list(EnhancedAttraction.get_collection().find({
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    '$maxDistance': max_distance
                }
            }
        }).limit(limit))

    @staticmethod
    def find_by_preferences(preferences, limit=5):
        query = {}

        if preferences.get('region'):
            query['region'] = preferences['region']

        if preferences.get('category'):
            # Map user category to attraction categories
            category_map = {
                'adventure': ['hiking', 'trekking', 'rafting', 'climbing', 'camping'],
                'cultural': ['heritage', 'museum', 'cultural_food', 'local_arts', 'village_life'],
                'historical': ['fort', 'mosque', 'old_city', 'archaeological', 'monument']
            }
            query['category'] = {'$in': category_map.get(preferences['category'], [])}

        return list(EnhancedAttraction.get_collection().find(query).limit(limit))


class EnhancedHotel:
    @staticmethod
    def get_collection():
        return mongo.db.hotels

    @staticmethod
    def find_nearby(lat, lng, max_distance=50000, limit=5):
        return list(EnhancedHotel.get_collection().find({
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    '$maxDistance': max_distance
                }
            }
        }).limit(limit))

    @staticmethod
    def find_by_budget(region, budget_range, limit=3):
        budget_map = {
            'low': (1000, 5000),
            'medium': (5000, 15000),
            'high': (15000, 50000)
        }

        min_price, max_price = budget_map.get(budget_range, (1000, 15000))

        return list(EnhancedHotel.get_collection().find({
            'region': region,
            'price_per_night': {'$gte': min_price, '$lte': max_price}
        }).limit(limit))


class EnhancedPackage:
    @staticmethod
    def get_collection():
        return mongo.db.packages

    @staticmethod
    def find_by_filters(filters):
        query = {}

        if filters.get('region'):
            query['region'] = filters['region']

        if filters.get('category'):
            query['category'] = filters['category']

        if filters.get('max_budget'):
            query['price'] = {'$lte': float(filters['max_budget'])}

        if filters.get('min_nights'):
            query['duration_days'] = {'$gte': int(filters['min_nights'])}

        return list(EnhancedPackage.get_collection().find(query))

    @staticmethod
    def get_categories():
        return ['adventure', 'cultural', 'historical', 'religious', 'beach']

    @staticmethod
    def get_regions():
        return ['northern', 'punjab', 'sindh', 'balochistan', 'kpk']

    @staticmethod
    def find_with_details(filters=None):
        pipeline = []

        if filters:
            match_stage = {}
            if filters.get('region'):
                match_stage['region'] = filters['region']
            if filters.get('category'):
                match_stage['category'] = filters['category']
            if filters.get('max_budget'):
                match_stage['price'] = {'$lte': float(filters['max_budget'])}
            if filters.get('min_nights'):
                match_stage['duration_days'] = {'$gte': int(filters['min_nights'])}

            if match_stage:
                pipeline.append({'$match': match_stage})

        # For hotels - match integer hotelID to package's hotels array
        pipeline.append({
            '$lookup': {
                'from': 'hotels',
                'let': {'hotel_ids': '$hotels'},  # Store package.hotels array
                'pipeline': [
                    {'$match': {
                        '$expr': {
                            '$in': ['$hotelID', '$$hotel_ids']  # Match hotelID in array
                        }
                    }}
                ],
                'as': 'hotel_details'
            }
        })

        # For attractions - match integer attractionID
        pipeline.append({
            '$lookup': {
                'from': 'attractions',
                'let': {'attraction_ids': '$attractions'},
                'pipeline': [
                    {'$match': {
                        '$expr': {
                            '$in': ['$attractionID', '$$attraction_ids']
                        }
                    }}
                ],
                'as': 'attraction_details'
            }
        })

        return list(EnhancedPackage.get_collection().aggregate(pipeline))