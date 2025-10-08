from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import get_db_connection
from config import Config
import functools
import os
from pathlib import Path

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Create upload folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
		"""Check if file extension is allowed"""
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
		"""View and edit user profile"""
		conn = get_db_connection()
		cur = conn.cursor()
		
		if request.method == 'POST':
				description = request.form.get('description', '').strip()
				
				# Handle avatar upload
				avatar_filename = None
				if 'avatar' in request.files:
						file = request.files['avatar']
						if file and file.filename and allowed_file(file.filename):
								# Create unique filename
								filename = secure_filename(file.filename)
								ext = filename.rsplit('.', 1)[1].lower()
								avatar_filename = f"user_{session['user_id']}.{ext}"
								file.save(os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename))
				
				# Update user profile
				if avatar_filename:
						cur.execute(
								'UPDATE users SET description = %s, avatar = %s WHERE id = %s',
								(description, avatar_filename, session['user_id'])
						)
				else:
						cur.execute(
								'UPDATE users SET description = %s WHERE id = %s',
								(description, session['user_id'])
						)
				
				conn.commit()
				flash('Profile updated successfully!', 'success')
				
				# Refresh user data
				cur.execute(
						'SELECT id, username, description, avatar FROM users WHERE id = %s',
						(session['user_id'],)
				)
				user = cur.fetchone()
				cur.close()
				conn.close()
				return render_template('profile.html', user=user, is_own_profile=True)
		
		# GET request - fetch user data
		cur.execute(
				'SELECT id, username, description, avatar FROM users WHERE id = %s',
				(session['user_id'],)
		)
		user = cur.fetchone()
		cur.close()
		conn.close()
		return render_template('profile.html', user=user, is_own_profile=True)


@app.route('/users')
@login_required
def users():
		"""View all users"""
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute(
				'SELECT id, username, description, avatar FROM users ORDER BY username'
		)
		all_users = cur.fetchall()
		cur.close()
		conn.close()
		return render_template('users.html', users=all_users)


@app.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
		"""View a specific user's profile"""
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute(
				'SELECT id, username, description, avatar FROM users WHERE id = %s',
				(user_id,)
		)
		user = cur.fetchone()
		cur.close()
		conn.close()
		
		if not user:
				flash('User not found', 'error')
				return redirect(url_for('users'))
		
		is_own_profile = (user_id == session['user_id'])
		return render_template('profile.html', user=user, is_own_profile=is_own_profile)


@app.route('/notes')
@login_required
def notes():
		"""List all notes for the current user"""
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute(
				'SELECT id, title, content, created_at, updated_at FROM notes WHERE user_id = %s ORDER BY updated_at DESC',
				(session['user_id'],)
		)
		user_notes = cur.fetchall()
		cur.close()
		conn.close()
		return render_template('notes.html', notes=user_notes)


@app.route('/notes/create', methods=['GET', 'POST'])
@login_required
def create_note():
		"""Create a new note"""
		if request.method == 'POST':
				title = request.form.get('title', '').strip()
				content = request.form.get('content', '').strip()
				
				# Validation
				if not title:
						flash('Title is required', 'error')
						return render_template('create_note.html')
				
				if len(title) > 200:
						flash('Title must be 200 characters or less', 'error')
						return render_template('create_note.html')
				
				# Create new note
				conn = get_db_connection()
				cur = conn.cursor()
				cur.execute(
						'INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s) RETURNING id',
						(session['user_id'], title, content)
				)
				note_id = cur.fetchone()['id']
				conn.commit()
				cur.close()
				conn.close()
				
				flash('Note created successfully!', 'success')
				return redirect(url_for('view_note', note_id=note_id))
		
		return render_template('create_note.html')


@app.route('/notes/<int:note_id>')
@login_required
def view_note(note_id):
		"""View a specific note"""
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute(
				'SELECT id, user_id, title, content, created_at, updated_at FROM notes WHERE id = %s',
				(note_id,)
		)
		note = cur.fetchone()
		cur.close()
		conn.close()
		
		if not note:
				flash('Note not found', 'error')
				return redirect(url_for('notes'))
		
		# Check if user owns this note
		if note['user_id'] != session['user_id']:
				flash('You do not have permission to view this note', 'error')
				return redirect(url_for('notes'))
		
		return render_template('note_detail.html', note=note)


if __name__ == '__main__':
		app.run(debug=True)

