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
						description TEXT,
						avatar VARCHAR(255),
						created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
		''')
		
		# Create notes table
		cur.execute('''
				CREATE TABLE IF NOT EXISTS notes (
						id SERIAL PRIMARY KEY,
						user_id INTEGER NOT NULL,
						title VARCHAR(200) NOT NULL,
						content TEXT,
						created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
						updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
						FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
				)
		''')
		
		conn.commit()
		cur.close()
		conn.close()
		print("Database initialized successfully!")


def migrate_db():
		"""Add new columns to existing users table"""
		conn = get_db_connection()
		cur = conn.cursor()
		
		# Add description column if it doesn't exist
		cur.execute("""
				DO $$ 
				BEGIN
						IF NOT EXISTS (
								SELECT 1 FROM information_schema.columns 
								WHERE table_name='users' AND column_name='description'
						) THEN
								ALTER TABLE users ADD COLUMN description TEXT;
						END IF;
				END $$;
		""")
		
		# Add avatar column if it doesn't exist
		cur.execute("""
				DO $$ 
				BEGIN
						IF NOT EXISTS (
								SELECT 1 FROM information_schema.columns 
								WHERE table_name='users' AND column_name='avatar'
						) THEN
								ALTER TABLE users ADD COLUMN avatar VARCHAR(255);
						END IF;
				END $$;
		""")
		
		conn.commit()
		cur.close()
		conn.close()
		print("Database migration completed successfully!")


if __name__ == '__main__':
		init_db()
		migrate_db()

