import os
from dotenv import load_dotenv

load_dotenv()


class Config:
		"""Application configuration"""
		# Security: Require SECRET_KEY to be set in production
		SECRET_KEY = os.getenv('SECRET_KEY')
		if not SECRET_KEY:
				raise ValueError("SECRET_KEY environment variable must be set")
		
		# Flask configuration
		DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
		TESTING = os.getenv('FLASK_TESTING', 'False').lower() == 'true'
		
		# Session security
		SESSION_COOKIE_HTTPONLY = True
		SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
		SESSION_COOKIE_SAMESITE = 'Lax'
		PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
		
		# Database configuration
		DB_HOST = os.getenv('DB_HOST', 'localhost')
		DB_PORT = os.getenv('DB_PORT', '5432')
		DB_USER = os.getenv('DB_USER', 'postgres')
		DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
		DB_NAME = os.getenv('DB_NAME', 'vibenotes1')
		
		# WTF CSRF protection
		WTF_CSRF_ENABLED = True
		WTF_CSRF_TIME_LIMIT = 3600

