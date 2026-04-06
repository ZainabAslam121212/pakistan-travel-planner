import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/pakistan_travel')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    HOTELS_API_KEY = os.getenv('HOTELS_API_KEY', '')