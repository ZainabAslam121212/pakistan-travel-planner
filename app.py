from flask import Flask, send_from_directory, jsonify
from models import mongo
from attractions import attractions_bp
from hotels import hotels_bp
from packages import packages_bp
from users import users_bp
from datetime import datetime
from config import Config

from flask_cors import CORS
# This should be after app creation
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    mongo.init_app(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(attractions_bp, url_prefix='/api')
    app.register_blueprint(hotels_bp, url_prefix='/api')
    app.register_blueprint(packages_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')

    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Pakistan Travel Planner API is running',
            'timestamp': datetime.utcnow().isoformat()
        })

    @app.route('/api')
    def api_info():
        return jsonify({
            'name': 'Pakistan Travel Planner API',
            'version': '1.0.0',
            'endpoints': {
                'attractions': '/api/attractions',
                'hotels': '/api/hotels',
                'packages': '/api/packages',
                'users': '/api/users'
            }
        })

    from flask import render_template

    @app.route('/')
    def serve_frontend():
        try:
            return send_from_directory('.', 'index.html')
        except:
            return jsonify({
                'message': 'Backend is running. Please open index.html directly in browser.',
                'api_docs': '/api'
            })

    @app.route('/<path:path>')
    def serve_static_files(path):
        try:
            return send_from_directory('.', path)
        except:
            return jsonify({'error': 'File not found'}), 404

    with app.app_context():
        initialize_database()

    return app


def initialize_database():
    """Initialize database with indexes and sample data"""
    try:
        # Create geospatial indexes
        mongo.db.hotels.create_index([("location", "2dsphere")])
        mongo.db.attractions.create_index([("location", "2dsphere")])
        print("✅ Geospatial indexes created successfully!")
    except Exception as e:
        print(f"⚠️ Index creation warning: {e}")

    print("📝 Note: Run seed_data.py separately to insert sample data, if not already done")



if __name__ == '__main__':
    app = create_app()
    print("🚀 Pakistan Travel Planner Backend Started!")
    print("📍 API available at: http://localhost:5000/api")
    print("🔍 Health check: http://localhost:5000/api/health")
    app.run(debug=True, host='0.0.0.0', port=5000)