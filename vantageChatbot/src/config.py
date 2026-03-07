import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./vantagechatbot.db')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'changeme')
CORS_ALLOW_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ALLOW_ORIGINS', '*').split(',') if origin.strip()]
