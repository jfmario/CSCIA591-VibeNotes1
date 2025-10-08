# VibeNotes

A simple web application for note-taking with user authentication built with Flask and PostgreSQL.

## Features

- User registration with username and password
- User login and logout functionality
- Session management
- Secure password hashing
- Clean and modern UI

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
		
		This will create the `users` table in your database.

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

## Project Structure

```
VibeNotes1/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database connection and initialization
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore file
├── README.md             # This file
├── static/
│   └── style.css         # CSS styles
└── templates/
    ├── base.html         # Base template
    ├── home.html         # Home page
    ├── login.html        # Login page
    └── register.html     # Registration page
```

## Database Schema

### users table
- `id`: SERIAL PRIMARY KEY
- `username`: VARCHAR(80) UNIQUE NOT NULL
- `password_hash`: VARCHAR(255) NOT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

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

