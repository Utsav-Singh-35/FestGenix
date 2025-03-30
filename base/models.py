from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ORGANIZER = 'ORGANIZER', _('Organizer')
        SPONSOR = 'SPONSOR', _('Sponsor')
        VOLUNTEER = 'VOLUNTEER', _('Volunteer')
        PARTICIPANT = 'PARTICIPANT', _('Participant')

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARTICIPANT)
    phone = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    available_days = models.JSONField(default=list, blank=True)
    time_preference = models.CharField(max_length=20, choices=[
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('flexible', 'Flexible'),
    ], default='flexible')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Add related_name to fix reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return self.email

class Event(models.Model):
    EVENT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    organizer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_events')
    volunteers = models.ManyToManyField(CustomUser, related_name='volunteered_events', blank=True)
    attendees = models.ManyToManyField(CustomUser, related_name='attended_events', blank=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_events')

    def __str__(self):
        return self.title

class Team(models.Model):
    name = models.CharField(max_length=100)
    sponsor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='teams')
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.department}"

class Budget(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='budget')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Budget for {self.event.title}"

class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - ${self.amount}"

class Report(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='report')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.event.title}"

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    attendee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ])
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'attendee']

    def __str__(self):
        return f"{self.attendee.full_name} - {self.event.name}"

class Skill(models.Model):
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='beginner')

    def __str__(self):
        return self.name

class Interest(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tasks')
    volunteer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    points = models.IntegerField(default=0)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
