import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config


def get_db_connection():
		"""Create and return a database connection"""
		conn = psycopg2.connect(
				host=Config.DB_HOST,
				port=Config.DB_PORT,
				user=Config.DB_USER,
				password=Config.DB_PASSWORD,
				database=Config.DB_NAME,
				cursor_factory=RealDictCursor
		)
		return conn


def init_db():
		"""Initialize the database with required tables"""
		conn = get_db_connection()
		cur = conn.cursor()
		
		# Create users table
		cur.execute('''
				CREATE TABLE IF NOT EXISTS users (
						id SERIAL PRIMARY KEY,
						username VARCHAR(80) UNIQUE NOT NULL,
						password_hash VARCHAR(255) NOT NULL,
						created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
		''')
		
		conn.commit()
		cur.close()
		conn.close()
		print("Database initialized successfully!")


if __name__ == '__main__':
		init_db()

