from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from config import Config
import functools

app = Flask(__name__)
app.config.from_object(Config)


def login_required(view):
		"""Decorator to require login for certain routes"""
		@functools.wraps(view)
		def wrapped_view(**kwargs):
				if 'user_id' not in session:
						return redirect(url_for('login'))
				return view(**kwargs)
		return wrapped_view


@app.route('/')
def index():
		"""Home page"""
		if 'user_id' in session:
				return render_template('home.html', username=session.get('username'))
		return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
		"""User registration"""
		if request.method == 'POST':
				username = request.form.get('username', '').strip()
				password = request.form.get('password', '')
				confirm_password = request.form.get('confirm_password', '')
				
				# Validation
				if not username or not password:
						flash('Username and password are required', 'error')
						return render_template('register.html')
				
				if len(username) < 3:
						flash('Username must be at least 3 characters long', 'error')
						return render_template('register.html')
				
				if len(password) < 6:
						flash('Password must be at least 6 characters long', 'error')
						return render_template('register.html')
				
				if password != confirm_password:
						flash('Passwords do not match', 'error')
						return render_template('register.html')
				
				# Check if username already exists
				conn = get_db_connection()
				cur = conn.cursor()
				cur.execute('SELECT id FROM users WHERE username = %s', (username,))
				existing_user = cur.fetchone()
				
				if existing_user:
						flash('Username already exists', 'error')
						cur.close()
						conn.close()
						return render_template('register.html')
				
				# Create new user
				password_hash = generate_password_hash(password)
				cur.execute(
						'INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id',
						(username, password_hash)
				)
				user_id = cur.fetchone()['id']
				conn.commit()
				cur.close()
				conn.close()
				
				# Log user in
				session['user_id'] = user_id
				session['username'] = username
				flash('Registration successful! Welcome to VibeNotes!', 'success')
				return redirect(url_for('index'))
		
		return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
		"""User login"""
		if request.method == 'POST':
				username = request.form.get('username', '').strip()
				password = request.form.get('password', '')
				
				if not username or not password:
						flash('Username and password are required', 'error')
						return render_template('login.html')
				
				# Find user
				conn = get_db_connection()
				cur = conn.cursor()
				cur.execute('SELECT id, username, password_hash FROM users WHERE username = %s', (username,))
				user = cur.fetchone()
				cur.close()
				conn.close()
				
				if user and check_password_hash(user['password_hash'], password):
						# Login successful
						session['user_id'] = user['id']
						session['username'] = user['username']
						flash('Login successful!', 'success')
						return redirect(url_for('index'))
				else:
						flash('Invalid username or password', 'error')
						return render_template('login.html')
		
		return render_template('login.html')


@app.route('/logout')
def logout():
		"""User logout"""
		session.clear()
		flash('You have been logged out', 'success')
		return redirect(url_for('login'))


if __name__ == '__main__':
		app.run(debug=True)

