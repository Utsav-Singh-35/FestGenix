from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser, Event, Team, Budget, Report, Attendance, Task, Skill, Interest
from django.db import models
from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import timedelta

def calculate_roi_data(events):
    """
    Calculate ROI data for the given events.
    Returns a dictionary containing:
    - Monthly ROI trend
    - Overall ROI
    - ROI by event status
    - Top performing events
    """
    roi_data = {
        'monthly_trend': [],
        'overall_roi': 0,
        'event_status_roi': {},
        'top_events': []
    }
    
    # Calculate overall ROI
    total_investment = sum(event.budget.amount for event in events if hasattr(event, 'budget'))
    total_revenue = sum(event.budget.amount * 1.2 for event in events if hasattr(event, 'budget'))  # Example revenue calculation
    
    if total_investment > 0:
        roi_data['overall_roi'] = ((total_revenue - total_investment) / total_investment) * 100
    
    # Calculate monthly ROI trend (last 6 months)
    current_date = timezone.now()
    for i in range(5, -1, -1):  # Last 6 months
        start_date = current_date - timedelta(days=(i+1)*30)
        end_date = current_date - timedelta(days=i*30)
        
        month_events = events.filter(start_date__range=[start_date, end_date])
        month_investment = sum(event.budget.amount for event in month_events if hasattr(event, 'budget'))
        month_revenue = sum(event.budget.amount * 1.2 for event in month_events if hasattr(event, 'budget'))
        
        month_roi = 0
        if month_investment > 0:
            month_roi = ((month_revenue - month_investment) / month_investment) * 100
        
        roi_data['monthly_trend'].append({
            'month': start_date.strftime('%B'),
            'roi': round(month_roi, 2)
        })
    
    # Calculate ROI by event status
    event_statuses = events.values('status').annotate(count=Count('id'))
    for event_status in event_statuses:
        status_events = events.filter(status=event_status['status'])
        status_investment = sum(event.budget.amount for event in status_events if hasattr(event, 'budget'))
        status_revenue = sum(event.budget.amount * 1.2 for event in status_events if hasattr(event, 'budget'))
        
        status_roi = 0
        if status_investment > 0:
            status_roi = ((status_revenue - status_investment) / status_investment) * 100
        
        roi_data['event_status_roi'][event_status['status']] = round(status_roi, 2)
    
    # Get top performing events (by ROI)
    top_events = sorted(
        [event for event in events if hasattr(event, 'budget')],
        key=lambda e: ((e.budget.amount * 1.2 - e.budget.amount) / e.budget.amount if e.budget.amount > 0 else 0),
        reverse=True
    )[:5]
    
    roi_data['top_events'] = [{
        'name': event.title,
        'date': event.start_date,
        'investment': event.budget.amount,
        'roi': round(((event.budget.amount * 1.2 - event.budget.amount) / event.budget.amount * 100), 2)
    } for event in top_events]
    
    return roi_data

def chatbot(request):
    return render(request, 'chatbot.html') 

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user role
                if user.role == CustomUser.Role.ORGANIZER:
                    return redirect('base:organizer_dashboard')
                elif user.role == CustomUser.Role.SPONSOR:
                    return redirect('base:sponsor_dashboard')
                elif user.role == CustomUser.Role.VOLUNTEER:
                    return redirect('base:volunteer_dashboard')
                else:
                    return redirect('base:participant_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'base/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            # Redirect based on user role
            if user.role == CustomUser.Role.ORGANIZER:
                return redirect('base:organizer_dashboard')
            elif user.role == CustomUser.Role.SPONSOR:
                return redirect('base:sponsor_dashboard')
            elif user.role == CustomUser.Role.VOLUNTEER:
                return redirect('base:volunteer_dashboard')
            else:
                return redirect('base:participant_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'base/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('base:login')

@login_required
def organizer_dashboard(request):
    if request.user.role != CustomUser.Role.ORGANIZER:
        messages.error(request, 'Access denied. Organizer privileges required.')
        return redirect('base:login')
    return render(request, 'dashboard/dashboard-organizer.html')

@login_required
def sponsor_dashboard(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    # Get teams where the user is a sponsor
    sponsor_teams = Team.objects.filter(sponsor=request.user)
    
    context = {
        'total_events': Event.objects.filter(team__in=sponsor_teams).count(),
        'sponsored_events': Event.objects.filter(team__in=sponsor_teams, status='published').count(),
        'total_investment': Budget.objects.filter(event__team__in=sponsor_teams).aggregate(total=models.Sum('amount'))['total'] or 0,
        'active_sponsorships': Event.objects.filter(team__in=sponsor_teams, status='published').count(),
    }
    return render(request, 'dashboard/dashboard-sponsor.html', context)

@login_required
def sponsor_sponsorship(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    # Get teams where the user is a sponsor
    sponsor_teams = Team.objects.filter(sponsor=request.user)
    events = Event.objects.filter(team__in=sponsor_teams)
    
    context = {
        'events': events,
        'active_sponsorships': events.filter(status='published').count(),
        'pending_sponsorships': events.filter(status='draft').count(),
        'completed_sponsorships': events.filter(status='completed').count(),
    }
    return render(request, 'dashboard/dashboard-sponsor-sponsorship.html', context)

@login_required
def sponsor_analytics(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    # Get teams where the user is a sponsor
    sponsor_teams = Team.objects.filter(sponsor=request.user)
    events = Event.objects.filter(team__in=sponsor_teams)
    
    context = {
        'total_events': events.count(),
        'total_attendees': sum(event.attendees.count() for event in events),
        'total_investment': Budget.objects.filter(event__team__in=sponsor_teams).aggregate(total=models.Sum('amount'))['total'] or 0,
        'roi_data': calculate_roi_data(events),
        'events': events,
    }
    return render(request, 'dashboard/dashboard-sponsor-analytics.html', context)

@login_required
def sponsor_team(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    team_members = Team.objects.filter(sponsor=request.user)
    context = {
        'team_members': team_members,
        'total_members': team_members.count(),
        'active_members': team_members.filter(status='active').count(),
        'departments': team_members.values('department').distinct().count(),
    }
    return render(request, 'dashboard/dashboard-sponsor-team.html', context)

@login_required
def sponsor_budget(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    budget = Budget.objects.filter(sponsor=request.user).first()
    expenses = budget.expenses.all() if budget else []
    
    context = {
        'budget': budget,
        'expenses': expenses,
        'total_budget': budget.total_amount if budget else 0,
        'amount_spent': sum(expense.amount for expense in expenses),
        'remaining_budget': (budget.total_amount - sum(expense.amount for expense in expenses)) if budget else 0,
    }
    return render(request, 'dashboard/dashboard-sponsor-budget.html', context)

@login_required
def sponsor_reports(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    reports = Report.objects.filter(sponsor=request.user)
    context = {
        'reports': reports,
        'total_reports': reports.count(),
        'performance_reports': reports.filter(type='performance').count(),
        'financial_reports': reports.filter(type='financial').count(),
    }
    return render(request, 'dashboard/dashboard-sponsor-reports.html', context)

@login_required
def sponsor_attendance(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    events = Event.objects.filter(sponsor=request.user)
    total_attendees = sum(event.attendees.count() for event in events)
    present_attendees = sum(event.attendees.filter(status='present').count() for event in events)
    
    context = {
        'events': events,
        'total_attendees': total_attendees,
        'present_attendees': present_attendees,
        'absent_attendees': total_attendees - present_attendees,
    }
    return render(request, 'dashboard/dashboard-sponsor-attendance.html', context)

@login_required
def sponsor_settings(request):
    if request.user.role != CustomUser.Role.SPONSOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('base:login')
    
    if request.method == 'POST':
        user = request.user
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.company_name = request.POST.get('company_name')
        user.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('base:sponsor_settings')
    
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard/dashboard-sponsor-settings.html', context)

@login_required
def volunteer_dashboard(request):
    if request.user.role != CustomUser.Role.VOLUNTEER:
        messages.error(request, 'Access denied. Volunteer privileges required.')
        return redirect('base:login')
    
    context = {
        'total_events': Event.objects.filter(volunteers=request.user).count(),
        'active_tasks': Task.objects.filter(volunteer=request.user, status='active').count(),
        'completed_tasks': Task.objects.filter(volunteer=request.user, status='completed').count(),
        'total_points': Task.objects.filter(volunteer=request.user, status='completed').aggregate(total=models.Sum('points'))['total'] or 0,
    }
    return render(request, 'dashboard/dashboard-volunteer.html', context)

@login_required
def volunteer_events(request):
    if request.user.role != CustomUser.Role.VOLUNTEER:
        messages.error(request, 'Access denied. Volunteer privileges required.')
        return redirect('base:login')
    
    context = {
        'upcoming_events': Event.objects.filter(
            start_date__gte=timezone.now(),
            volunteers=request.user
        ).order_by('start_date'),
        'past_events': Event.objects.filter(
            start_date__lt=timezone.now(),
            volunteers=request.user
        ).order_by('-start_date'),
    }
    return render(request, 'dashboard/dashboard-volunteer-events.html', context)

@login_required
def volunteer_tasks(request):
    if request.user.role != CustomUser.Role.VOLUNTEER:
        messages.error(request, 'Access denied. Volunteer privileges required.')
        return redirect('base:login')
    
    context = {
        'pending_tasks_count': Task.objects.filter(volunteer=request.user, status='pending').count(),
        'in_progress_tasks_count': Task.objects.filter(volunteer=request.user, status='in_progress').count(),
        'completed_tasks_count': Task.objects.filter(volunteer=request.user, status='completed').count(),
        'total_points': Task.objects.filter(volunteer=request.user, status='completed').aggregate(total=models.Sum('points'))['total'] or 0,
        'active_tasks': Task.objects.filter(volunteer=request.user, status__in=['pending', 'in_progress']),
        'completed_tasks': Task.objects.filter(volunteer=request.user, status='completed'),
    }
    return render(request, 'dashboard/dashboard-volunteer-tasks.html', context)

@login_required
def volunteer_settings(request):
    if request.user.role != CustomUser.Role.VOLUNTEER:
        messages.error(request, 'Access denied. Volunteer privileges required.')
        return redirect('base:login')
    
    if request.method == 'POST':
        user = request.user
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.location = request.POST.get('location')
        user.save()
        
        # Handle skills and interests
        user.skills.set(request.POST.getlist('skills'))
        user.interests.set(request.POST.getlist('interests'))
        
        # Handle availability
        user.available_days = request.POST.getlist('available_days')
        user.time_preference = request.POST.get('time_preference')
        
        # Handle notifications
        user.email_notifications = request.POST.get('email_notifications') == 'on'
        user.sms_notifications = request.POST.get('sms_notifications') == 'on'
        
        # Handle password change if provided
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        if current_password and new_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully!')
            else:
                messages.error(request, 'Current password is incorrect.')
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('base:volunteer_settings')
    
    context = {
        'volunteer': request.user,
        'available_skills': Skill.objects.all(),
        'available_interests': Interest.objects.all(),
        'days_of_week': [
            {'value': 'monday', 'label': 'Monday'},
            {'value': 'tuesday', 'label': 'Tuesday'},
            {'value': 'wednesday', 'label': 'Wednesday'},
            {'value': 'thursday', 'label': 'Thursday'},
            {'value': 'friday', 'label': 'Friday'},
            {'value': 'saturday', 'label': 'Saturday'},
            {'value': 'sunday', 'label': 'Sunday'},
        ],
    }
    return render(request, 'dashboard/dashboard-volunteer-settings.html', context)

@login_required
def participant_dashboard(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    context = {
        'upcoming_events': Event.objects.filter(
            start_date__gte=timezone.now(),
            attendees=request.user
        ).order_by('start_date')[:3],
        'total_events_attended': Event.objects.filter(
            attendees=request.user,
            start_date__lt=timezone.now()
        ).count(),
        'rewards_points': 0,  # TODO: Implement rewards system
        'membership_level': 'Silver'  # TODO: Implement membership levels
    }
    return render(request, 'dashboard/dashboard-participant.html', context)

@login_required
def participant_my_events(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    context = {
        'upcoming_events': Event.objects.filter(
            start_date__gte=timezone.now(),
            attendees=request.user
        ).order_by('start_date'),
        'past_events': Event.objects.filter(
            start_date__lt=timezone.now(),
            attendees=request.user
        ).order_by('-start_date')
    }
    return render(request, 'dashboard/dashboard-participant-events.html', context)

@login_required
def participant_rewards(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    context = {
        'total_points': 0,  # TODO: Implement rewards system
        'available_rewards': [],  # TODO: Implement rewards
        'redeemed_rewards': [],
        'membership_level': 'Silver'
    }
    return render(request, 'dashboard/dashboard-participant-rewards.html', context)

@login_required
def participant_explore(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    context = {
        'upcoming_events': Event.objects.filter(
            start_date__gte=timezone.now(),
            status='published'
        ).exclude(attendees=request.user).order_by('start_date'),
        'recommended_events': Event.objects.filter(
            start_date__gte=timezone.now(),
            status='published'
        ).exclude(attendees=request.user).order_by('?')[:5]  # Random selection for now
    }
    return render(request, 'dashboard/dashboard-participant-explore.html', context)

@login_required
def participant_history(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    context = {
        'event_history': Event.objects.filter(
            attendees=request.user
        ).order_by('-start_date'),
        'total_events': Event.objects.filter(attendees=request.user).count(),
        'this_month_events': Event.objects.filter(
            attendees=request.user,
            start_date__month=timezone.now().month
        ).count()
    }
    return render(request, 'dashboard/dashboard-participant-history.html', context)

@login_required
def participant_feedback(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        # TODO: Implement feedback submission
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('base:participant_feedback')
    
    context = {
        'recent_events': Event.objects.filter(
            attendees=request.user,
            start_date__lt=timezone.now()
        ).order_by('-start_date')[:5]
    }
    return render(request, 'dashboard/dashboard-participant-feedback.html', context)

@login_required
def participant_profile(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    if request.method == 'POST':
        user = request.user
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.location = request.POST.get('location')
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        
        # Handle interests
        user.interests.set(request.POST.getlist('interests'))
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('base:participant_profile')
    
    context = {
        'user': request.user,
        'available_interests': Interest.objects.all()
    }
    return render(request, 'dashboard/dashboard-participant-profile.html', context)

@login_required
def participant_settings(request):
    if request.user.role != CustomUser.Role.PARTICIPANT:
        messages.error(request, 'Access denied. Participant privileges required.')
        return redirect('base:login')
    
    if request.method == 'POST':
        user = request.user
        
        # Handle notification preferences
        user.email_notifications = request.POST.get('email_notifications') == 'on'
        user.sms_notifications = request.POST.get('sms_notifications') == 'on'
        
        # Handle password change if provided
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        if current_password and new_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully!')
            else:
                messages.error(request, 'Current password is incorrect.')
        
        user.save()
        messages.success(request, 'Settings updated successfully!')
        return redirect('base:participant_settings')
    
    context = {
        'user': request.user
    }
    return render(request, 'dashboard/dashboard-participant-settings.html', context)

def home(request):
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on role
        if request.user.role == CustomUser.Role.ORGANIZER:
            return redirect('base:organizer_dashboard')
        elif request.user.role == CustomUser.Role.SPONSOR:
            return redirect('base:sponsor_dashboard')
        elif request.user.role == CustomUser.Role.VOLUNTEER:
            return redirect('base:volunteer_dashboard')
        else:
            return redirect('base:participant_dashboard')
    return render(request, 'base/home.html')

@login_required
def events_dashboard(request):
    return render(request, 'dashboard/dashboard-events.html')

@login_required
def reports_dashboard(request):
    if request.user.role != CustomUser.Role.ORGANIZER:
        messages.error(request, 'Access denied. Organizer privileges required.')
        return redirect('base:login')
    return render(request, 'dashboard/dashboard-reports.html')

@login_required
def attendance_dashboard(request):
    if request.user.role != CustomUser.Role.ORGANIZER:
        messages.error(request, 'Access denied. Organizer privileges required.')
        return redirect('base:login')
    return render(request, 'dashboard/dashboard-attendance.html')

@login_required
def settings_dashboard(request):
    return render(request, 'dashboard/dashboard-settings.html')

@login_required
def team_dashboard(request):
    if request.user.role != CustomUser.Role.ORGANIZER:
        messages.error(request, 'Access denied. Organizer privileges required.')
        return redirect('base:login')
    return render(request, 'dashboard/dashboard-team.html')

@login_required
def budget_dashboard(request):
    if request.user.role != CustomUser.Role.ORGANIZER:
        messages.error(request, 'Access denied. Organizer privileges required.')
        return redirect('base:login')
    return render(request, 'dashboard/dashboard-budget.html')

