# EventAI Project Setup Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git
- Virtual environment tool (venv or virtualenv)

## 1. Clone the Repository
```bash
git clone <repository-url>
cd FestGenix
```

## 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
```

## 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

## 4. Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 5. Database Setup
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 6. Static Files
```bash
# Collect static files
python manage.py collectstatic
```

## 7. Project Structure
Ensure the following directory structure:
```
FestGenix/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── static/
│   ├── css/
│   │   ├── participant-dashboard.css
│   │   └── participant-feedback.css
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   └── dashboard/
│       ├── base_participant.html
│       ├── dashboard-participant.html
│       ├── dashboard-participant-feedback.html
│       ├── participant-profile.html
│       └── participant-settings.html
└── base/
    ├── __init__.py
    ├── admin.py
    ├── models.py
    ├── views.py
    └── urls.py
```

## 8. URL Configuration
Add the following to `base/urls.py`:
```python
from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.participant_dashboard, name='participant_dashboard'),
    path('dashboard/my-events/', views.participant_my_events, name='participant_my_events'),
    path('dashboard/rewards/', views.participant_rewards, name='participant_rewards'),
    path('dashboard/explore/', views.participant_explore, name='participant_explore'),
    path('dashboard/history/', views.participant_history, name='participant_history'),
    path('dashboard/feedback/', views.participant_feedback, name='participant_feedback'),
    path('dashboard/profile/', views.participant_profile, name='participant_profile'),
    path('dashboard/settings/', views.participant_settings, name='participant_settings'),
    path('logout/', views.logout_view, name='logout'),
]
```

## 9. Models Setup
Add the following to `base/models.py`:
```python
from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
```

## 10. Run Development Server
```bash
# Start the development server
python manage.py runserver
```
Access the application at `http://localhost:8000`

## 11. Additional Configuration

### Email Setup (Optional)
For email functionality, update `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Static Files Configuration
In `settings.py`:
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

## 12. Testing
```bash
# Run tests
python manage.py test
```

## 13. Security Checklist
- [ ] Update SECRET_KEY in production
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set up proper database in production
- [ ] Configure proper static file serving
- [ ] Set up proper email backend
- [ ] Enable CSRF protection
- [ ] Set up proper logging

## 14. Deployment Considerations
1. Choose a hosting platform (e.g., Heroku, DigitalOcean, AWS)
2. Set up production database
3. Configure static file serving
4. Set up domain and SSL
5. Configure environment variables
6. Set up monitoring and logging
7. Configure backup system

## Common Issues and Solutions

### Static Files Not Loading
1. Check STATIC_URL and STATICFILES_DIRS in settings.py
2. Run collectstatic
3. Check file permissions

### Database Migrations
1. If you get migration errors:
```bash
python manage.py migrate --fake-initial
```

### Permission Issues
1. Check file permissions
2. Ensure proper user access to directories

## Maintenance Tasks

### Regular Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Make and apply migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

### Backup Database
```bash
# Create database backup
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json
``` 