from django.contrib import admin
from django.urls import path
from . import views

app_name = 'base'  # Add namespace

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('dashboard/sponsor/', views.sponsor_dashboard, name='sponsor_dashboard'),
    path('dashboard/volunteer/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('volunteer/events/', views.volunteer_events, name='volunteer_events'),
    path('volunteer/tasks/', views.volunteer_tasks, name='volunteer_tasks'),
    path('volunteer/settings/', views.volunteer_settings, name='volunteer_settings'),
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),
    path('participant/events/', views.participant_my_events, name='participant_my_events'),
    path('participant/rewards/', views.participant_rewards, name='participant_rewards'),
    path('participant/explore/', views.participant_explore, name='participant_explore'),
    path('participant/history/', views.participant_history, name='participant_history'),
    path('participant/feedback/', views.participant_feedback, name='participant_feedback'),
    path('participant/profile/', views.participant_profile, name='participant_profile'),
    path('participant/settings/', views.participant_settings, name='participant_settings'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('dashboard/events/', views.events_dashboard, name='events_dashboard'),
    path('dashboard/reports/', views.reports_dashboard, name='reports_dashboard'),
    path('dashboard/attendance/', views.attendance_dashboard, name='attendance_dashboard'),
    path('dashboard/settings/', views.settings_dashboard, name='settings_dashboard'),
    path('dashboard/team/', views.team_dashboard, name='team_dashboard'),
    path('dashboard/budget/', views.budget_dashboard, name='budget_dashboard'),
    path('sponsor/dashboard/', views.sponsor_dashboard, name='sponsor_dashboard'),
    path('sponsor/sponsorship/', views.sponsor_sponsorship, name='sponsor_sponsorship'),
    path('sponsor/analytics/', views.sponsor_analytics, name='sponsor_analytics'),
    path('sponsor/settings/', views.sponsor_settings, name='sponsor_settings'),
]
