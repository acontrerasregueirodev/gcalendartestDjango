from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('google-auth/', views.google_auth, name='google_auth'),
    path('oauth2callback', views.oauth2callback, name='oauth2callback'),
    path('calendar/', views.get_calendar_events, name='calendar'),
]
