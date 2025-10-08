from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import get_db_connection
from config import Config
import functools
import os
import uuid
from pathlib import Path

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'avatars')
ATTACHMENTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'attachments')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_ATTACHMENT_EXTENSIONS = {
		'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx',
		'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg',
		'zip', 'rar', '7z',
		'mp3', 'wav', 'mp4', 'avi', 'mov',
		'csv', 'json', 'xml'
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ATTACHMENTS_FOLDER'] = ATTACHMENTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Create upload folders if they don't exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(ATTACHMENTS_FOLDER).mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
		"""Check if file extension is allowed for avatars"""
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_attachment(filename):
		"""Check if file extension is allowed for attachments"""
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_ATTACHMENT_EXTENSIONS


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
				
				# Handle file attachments
				if 'attachments' in request.files:
						files = request.files.getlist('attachments')
						for file in files:
								if file and file.filename and allowed_attachment(file.filename):
										# Generate unique filename
										original_filename = secure_filename(file.filename)
										ext = original_filename.rsplit('.', 1)[1].lower()
										unique_filename = f"{uuid.uuid4().hex}.{ext}"
										file_path = os.path.join(app.config['ATTACHMENTS_FOLDER'], unique_filename)
										file.save(file_path)
										
										# Get file size
										file_size = os.path.getsize(file_path)
										
										# Save attachment info to database
										cur.execute(
												'INSERT INTO attachments (note_id, filename, original_filename, file_size) VALUES (%s, %s, %s, %s)',
												(note_id, unique_filename, original_filename, file_size)
										)
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
		
		if not note:
				cur.close()
				conn.close()
				flash('Note not found', 'error')
				return redirect(url_for('notes'))
		
		# Check if user owns this note
		if note['user_id'] != session['user_id']:
				cur.close()
				conn.close()
				flash('You do not have permission to view this note', 'error')
				return redirect(url_for('notes'))
		
		# Get attachments for this note
		cur.execute(
				'SELECT id, filename, original_filename, file_size, uploaded_at FROM attachments WHERE note_id = %s ORDER BY uploaded_at',
				(note_id,)
		)
		attachments = cur.fetchall()
		
		cur.close()
		conn.close()
		
		return render_template('note_detail.html', note=note, attachments=attachments)


@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
		"""Edit an existing note"""
		conn = get_db_connection()
		cur = conn.cursor()
		
		# Get the note
		cur.execute(
				'SELECT id, user_id, title, content FROM notes WHERE id = %s',
				(note_id,)
		)
		note = cur.fetchone()
		
		if not note:
				cur.close()
				conn.close()
				flash('Note not found', 'error')
				return redirect(url_for('notes'))
		
		# Check if user owns this note
		if note['user_id'] != session['user_id']:
				cur.close()
				conn.close()
				flash('You do not have permission to edit this note', 'error')
				return redirect(url_for('notes'))
		
		if request.method == 'POST':
				title = request.form.get('title', '').strip()
				content = request.form.get('content', '').strip()
				
				# Validation
				if not title:
						flash('Title is required', 'error')
						cur.close()
						conn.close()
						return render_template('edit_note.html', note=note)
				
				if len(title) > 200:
						flash('Title must be 200 characters or less', 'error')
						cur.close()
						conn.close()
						return render_template('edit_note.html', note=note)
				
				# Update the note
				cur.execute(
						'UPDATE notes SET title = %s, content = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
						(title, content, note_id)
				)
				conn.commit()
				
				# Handle file attachments
				if 'attachments' in request.files:
						files = request.files.getlist('attachments')
						for file in files:
								if file and file.filename and allowed_attachment(file.filename):
										# Generate unique filename
										original_filename = secure_filename(file.filename)
										ext = original_filename.rsplit('.', 1)[1].lower()
										unique_filename = f"{uuid.uuid4().hex}.{ext}"
										file_path = os.path.join(app.config['ATTACHMENTS_FOLDER'], unique_filename)
										file.save(file_path)
										
										# Get file size
										file_size = os.path.getsize(file_path)
										
										# Save attachment info to database
										cur.execute(
												'INSERT INTO attachments (note_id, filename, original_filename, file_size) VALUES (%s, %s, %s, %s)',
												(note_id, unique_filename, original_filename, file_size)
										)
										conn.commit()
				
				cur.close()
				conn.close()
				
				flash('Note updated successfully!', 'success')
				return redirect(url_for('view_note', note_id=note_id))
		
		cur.close()
		conn.close()
		return render_template('edit_note.html', note=note)


@app.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
		"""Delete a note"""
		conn = get_db_connection()
		cur = conn.cursor()
		
		# Get the note
		cur.execute(
				'SELECT id, user_id FROM notes WHERE id = %s',
				(note_id,)
		)
		note = cur.fetchone()
		
		if not note:
				cur.close()
				conn.close()
				flash('Note not found', 'error')
				return redirect(url_for('notes'))
		
		# Check if user owns this note
		if note['user_id'] != session['user_id']:
				cur.close()
				conn.close()
				flash('You do not have permission to delete this note', 'error')
				return redirect(url_for('notes'))
		
		# Delete the note (cascade will delete attachments and their files)
		# Get attachments to delete files from disk
		cur.execute('SELECT filename FROM attachments WHERE note_id = %s', (note_id,))
		attachments = cur.fetchall()
		for attachment in attachments:
				file_path = os.path.join(app.config['ATTACHMENTS_FOLDER'], attachment['filename'])
				if os.path.exists(file_path):
						os.remove(file_path)
		
		cur.execute('DELETE FROM notes WHERE id = %s', (note_id,))
		conn.commit()
		cur.close()
		conn.close()
		
		flash('Note deleted successfully!', 'success')
		return redirect(url_for('notes'))


@app.route('/attachments/<int:attachment_id>/download')
@login_required
def download_attachment(attachment_id):
		"""Download an attachment"""
		conn = get_db_connection()
		cur = conn.cursor()
		
		# Get attachment and note info
		cur.execute(
				'SELECT a.filename, a.original_filename, n.user_id FROM attachments a JOIN notes n ON a.note_id = n.id WHERE a.id = %s',
				(attachment_id,)
		)
		attachment = cur.fetchone()
		cur.close()
		conn.close()
		
		if not attachment:
				flash('Attachment not found', 'error')
				return redirect(url_for('notes'))
		
		# Check if user owns the note this attachment belongs to
		if attachment['user_id'] != session['user_id']:
				flash('You do not have permission to access this attachment', 'error')
				return redirect(url_for('notes'))
		
		return send_from_directory(
				app.config['ATTACHMENTS_FOLDER'],
				attachment['filename'],
				as_attachment=True,
				download_name=attachment['original_filename']
		)


@app.route('/attachments/<int:attachment_id>/delete', methods=['POST'])
@login_required
def delete_attachment(attachment_id):
		"""Delete an attachment"""
		conn = get_db_connection()
		cur = conn.cursor()
		
		# Get attachment and note info
		cur.execute(
				'SELECT a.filename, a.note_id, n.user_id FROM attachments a JOIN notes n ON a.note_id = n.id WHERE a.id = %s',
				(attachment_id,)
		)
		attachment = cur.fetchone()
		
		if not attachment:
				cur.close()
				conn.close()
				flash('Attachment not found', 'error')
				return redirect(url_for('notes'))
		
		# Check if user owns the note this attachment belongs to
		if attachment['user_id'] != session['user_id']:
				cur.close()
				conn.close()
				flash('You do not have permission to delete this attachment', 'error')
				return redirect(url_for('notes'))
		
		# Delete file from disk
		file_path = os.path.join(app.config['ATTACHMENTS_FOLDER'], attachment['filename'])
		if os.path.exists(file_path):
				os.remove(file_path)
		
		# Delete from database
		cur.execute('DELETE FROM attachments WHERE id = %s', (attachment_id,))
		conn.commit()
		cur.close()
		conn.close()
		
		flash('Attachment deleted successfully!', 'success')
		return redirect(url_for('view_note', note_id=attachment['note_id']))


if __name__ == '__main__':
		app.run(debug=True)

