# FestGenix

FestGenix is a comprehensive event management platform built with Django that helps organizers create and manage events while providing participants with an intuitive interface to discover and register for events.

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Utsav-Singh-35/FestGenix.git
cd FestGenix
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url  # For production
AWS_ACCESS_KEY_ID=your-aws-access-key  # For production
AWS_SECRET_ACCESS_KEY=your-aws-secret-key  # For production
AWS_STORAGE_BUCKET_NAME=your-bucket-name  # For production
```

5. Run database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Features

- Modern dark theme interface with responsive design
- Event creation and management for organizers
- Event discovery and registration for participants
- Reward system for event participation
- User dashboard with event history and analytics
- QR code generation for event check-ins
- AI-powered event recommendations
- Secure authentication and authorization
- File upload and management
- Real-time event updates

## Tech Stack

- Django 5.1.7
- Python 3.13
- SQLite (Development) / PostgreSQL (Production)
- HTML5/CSS3
- JavaScript
- Bootstrap 5
- Feather Icons
- Google Generative AI
- AWS S3 (for production file storage)

## Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git

## Project Structure

```
FestGenix/
├── base/                 # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # URL routing
│   └── forms.py         # Form definitions
├── templates/           # HTML templates
├── static/             # Static files (CSS, JS, images)
├── media/              # User-uploaded files
├── FestGenix/          # Project settings
├── manage.py           # Django management script
└── requirements.txt    # Project dependencies
```

## Development Guidelines

1. Follow PEP 8 style guide for Python code
2. Write docstrings for all functions and classes
3. Create unit tests for new features
4. Use meaningful commit messages
5. Keep the code modular and maintainable

## Deployment

For production deployment:

1. Set `DEBUG=False` in settings.py
2. Configure a production-grade database (PostgreSQL recommended)
3. Set up AWS S3 for file storage
4. Configure proper security settings
5. Use environment variables for sensitive data
6. Set up proper logging
7. Use a production-grade server (Gunicorn recommended)
8. Configure proper CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Django framework and its contributors
- Bootstrap team for the UI framework
- All contributors to this project 