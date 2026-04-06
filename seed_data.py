from app import create_app
from models import mongo
import json
import os
from bson import ObjectId


def seed_enhanced_data():
    app = create_app()

    with app.app_context():
        print("🚀 Starting enhanced data seeding...")

        # Read JSON files
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Load attractions data
        try:
            with open(os.path.join(base_dir, 'sample_attractions.json'), 'r', encoding='utf-8') as f:
                attractions_data = json.load(f)
            print(f"📊 Loaded {len(attractions_data)} attractions from JSON")
        except FileNotFoundError:
            print("❌ sample_attractions.json not found. Skipping attractions.")
            attractions_data = []

        # Load hotels data
        try:
            with open(os.path.join(base_dir, 'sample_hotels.json'), 'r', encoding='utf-8') as f:
                hotels_data = json.load(f)
            print(f"🏨 Loaded {len(hotels_data)} hotels from JSON")
        except FileNotFoundError:
            print("❌ sample_hotels.json not found. Skipping hotels.")
            hotels_data = []

        # Load packages data
        try:
            with open(os.path.join(base_dir, 'sample_packages.json'), 'r', encoding='utf-8') as f:
                packages_data = json.load(f)
            print(f"📦 Loaded {len(packages_data)} packages from JSON")
        except FileNotFoundError:
            print("❌ sample_packages.json not found. Skipping packages.")
            packages_data = []

        # Insert attractions if they don't exist
        if attractions_data:
            attractions_inserted = 0
            for attraction in attractions_data:
                # Check if attraction already exists by name
                existing = mongo.db.attractions.find_one({'name': attraction['name']})
                if not existing:
                    if 'attractionID' in attraction:
                        attraction['attractionID'] = attraction['attractionID']
                    # Ensure location has correct format
                    if 'location' in attraction and 'coordinates' in attraction['location']:
                        # MongoDB expects [lng, lat] for GeoJSON
                        attraction['location']['coordinates'] = attraction['location']['coordinates']
                    mongo.db.attractions.insert_one(attraction)
                    attractions_inserted += 1
            print(
                f"✅ Inserted {attractions_inserted} new attractions (skipped {len(attractions_data) - attractions_inserted} duplicates)")

        # Insert hotels if they don't exist
        if hotels_data:
            hotels_inserted = 0
            for hotel in hotels_data:
                # Check if hotel already exists by hotelName (or name field)
                existing = mongo.db.hotels.find_one({'name': hotel.get('hotelName')})
                if not existing:
                    if 'hotelID' in hotel:
                        hotel['hotelID'] = hotel['hotelID']  # Keep as integer
                    if 'name' in hotel:
                        hotel['name'] = hotel['name']
                    # Ensure location has correct format
                    if 'location' in hotel and 'coordinates' in hotel['location']:
                        # MongoDB expects [lng, lat] for GeoJSON
                        hotel['location']['coordinates'] = hotel['location']['coordinates']
                    # Add region field if not present (extract from description or set default)
                    if 'region' not in hotel:
                        hotel['region'] = 'northern'  # Default
                    # Add price_per_night field if not present (extract from priceRange)
                    if 'price_per_night' not in hotel and 'priceRange' in hotel:
                        try:
                            # Extract numeric value from price range string
                            price_str = hotel['priceRange'].split('-')[0].replace('PKR', '').replace(',', '').strip()
                            hotel['price_per_night'] = int(price_str)
                        except:
                            hotel['price_per_night'] = 8000  # Default
                    mongo.db.hotels.insert_one(hotel)
                    hotels_inserted += 1
            print(f"✅ Inserted {hotels_inserted} new hotels (skipped {len(hotels_data) - hotels_inserted} duplicates)")

        # Insert packages if they don't exist
        if packages_data:
            packages_inserted = 0
            for package in packages_data:
                # Check if package already exists by name
                existing = mongo.db.packages.find_one({'name': package['name']})
                if not existing:
                    # Remove any 'id' field if present
                    if 'id' in package:
                        del package['id']
                    mongo.db.packages.insert_one(package)
                    packages_inserted += 1
            print(
                f"✅ Inserted {packages_inserted} new packages (skipped {len(packages_data) - packages_inserted} duplicates)")

        print("\n📈 Database Summary:")
        print(f"📊 Total attractions in database: {mongo.db.attractions.count_documents({})}")
        print(f"🏨 Total hotels in database: {mongo.db.hotels.count_documents({})}")
        print(f"📦 Total packages in database: {mongo.db.packages.count_documents({})}")

        # Create geospatial indexes if they don't exist
        try:
            mongo.db.hotels.create_index([("location", "2dsphere")])
            mongo.db.attractions.create_index([("location", "2dsphere")])
            print("\n✅ Geospatial indexes created/verified!")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")


if __name__ == '__main__':
    seed_enhanced_data()