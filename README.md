# VibeNotes

A simple web application for note-taking with user authentication built with Flask and PostgreSQL.

## Features

- User registration with username and password
- User login and logout functionality
- **Notes Management:**
  - Create notes with title and content
  - Edit your existing notes
  - Delete notes with confirmation
  - Mark notes as public to share them on your profile
  - Attach files to notes (PDF, docs, images, archives, etc.)
  - Download and delete attachments
  - View all your notes in a grid layout
  - View detailed note pages
  - Notes are sorted by most recently updated
- User profiles with custom descriptions and avatars
- Avatar upload (supports PNG, JPG, JPEG, GIF up to 10MB)
- File attachments support (PDF, Office docs, images, archives, media files up to 10MB)
- Browse and view other users' profiles
- Public notes displayed on user profiles
- Read-only access to other users' public notes
- Session management
- Secure password hashing
- Clean and modern UI with responsive design

## Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS
- **Security**: Werkzeug for password hashing

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository or navigate to the project directory**

2. **Create a virtual environment** (recommended)
		```bash
		python -m venv venv
		source venv/bin/activate  # On Windows: venv\Scripts\activate
		```

3. **Install dependencies**
		```bash
		pip install -r requirements.txt
		```

4. **Set up environment variables**
		
		Create a `.env` file in the root directory with the following content:
		```
		DB_HOST=localhost
		DB_PORT=5432
		DB_USER=postgres
		DB_PASSWORD=password
		DB_NAME=vibenotes1
		SECRET_KEY=your-secret-key-change-in-production
		```
		
		**Important**: Change the `SECRET_KEY` to a random string in production!

5. **Initialize the database**
		
		Make sure your PostgreSQL database is running and accessible with the credentials in your `.env` file.
		
		Run the database initialization script:
		```bash
		python database.py
		```
		
		This will create the `users` table in your database with all necessary columns (including `description` and `avatar` for profiles).
		
		**Note**: If you're upgrading from an older version, running `python database.py` will automatically migrate your existing database to add the new profile columns.

## Running the Application

1. **Start the Flask development server**
		```bash
		python app.py
		```

2. **Access the application**
		
		Open your web browser and navigate to:
		```
		http://localhost:5000
		```

3. **Register a new account**
		
		Click on "Register here" to create a new account with a username and password.

4. **Login**
		
		Use your credentials to log in to the application.

5. **Customize your profile**
		
		Navigate to "My Profile" to add a description and upload an avatar.

6. **Create and manage notes**
		
		Click "My Notes" or "Create Note" to start writing and organizing your notes.

7. **Browse other users**
		
		Visit the "Users" page to see other members and their profiles.

## Project Structure

```
VibeNotes1/
├── app.py                 # Main Flask application with all routes
├── config.py              # Configuration settings
├── database.py            # Database connection and initialization
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore file
├── README.md             # This file
├── static/
│   ├── style.css         # CSS styles
│   ├── avatars/          # User avatar uploads (created automatically)
│   └── attachments/      # Note file attachments (created automatically)
└── templates/
    ├── base.html         # Base template with navigation
    ├── home.html         # Home page with quick actions
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── profile.html      # User profile view/edit page
    ├── users.html        # Users list page
    ├── notes.html        # Notes list page
    ├── create_note.html  # Create note form
    ├── edit_note.html    # Edit note form
    └── note_detail.html  # Note detail view page
```

## Database Schema

### users table
- `id`: SERIAL PRIMARY KEY
- `username`: VARCHAR(80) UNIQUE NOT NULL
- `password_hash`: VARCHAR(255) NOT NULL
- `description`: TEXT (user's profile description)
- `avatar`: VARCHAR(255) (filename of user's avatar image)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### notes table
- `id`: SERIAL PRIMARY KEY
- `user_id`: INTEGER NOT NULL (foreign key to users.id)
- `title`: VARCHAR(200) NOT NULL
- `content`: TEXT
- `is_public`: BOOLEAN DEFAULT FALSE (whether the note is visible on user's profile)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### attachments table
- `id`: SERIAL PRIMARY KEY
- `note_id`: INTEGER NOT NULL (foreign key to notes.id)
- `filename`: VARCHAR(255) NOT NULL (unique filename on disk)
- `original_filename`: VARCHAR(255) NOT NULL (original user-provided filename)
- `file_size`: INTEGER (size in bytes)
- `uploaded_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Security Notes

- Passwords are hashed using Werkzeug's security functions (PBKDF2-based)
- Session management is handled by Flask's built-in session system
- The SECRET_KEY should be changed to a random, secure value in production
- Never commit the `.env` file to version control

## Development

To run in development mode with debug enabled:
```bash
python app.py
```

For production deployment, use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn app:app
```

## License

This project is open source and available for personal and educational use.

