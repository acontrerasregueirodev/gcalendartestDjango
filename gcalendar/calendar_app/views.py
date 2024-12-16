import os
import json
from django.shortcuts import redirect, render
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.http import HttpResponse
from .utils.google_calendar import list_events


# Ruta al archivo de credenciales JSON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']  # Permiso solo lectura del calendario

def google_auth(request):
    # Inicia el flujo de autenticación de OAuth
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/oauth2callback'  # Cambia esta URL si tu dominio cambia
    )

    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

def oauth2callback(request):
    # Obtener el código de autorización de la URL
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Error: No se recibió el código de autorización.")

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/oauth2callback'
    )
    flow.fetch_token(code=code)

    credentials = flow.credentials
    # Guardar las credenciales en la sesión
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return redirect('/calendar')


def home(request):
    events = list_events()  # Llamar a la función
    return render(request, 'calendar_app/home.html', {'events': events})

def get_calendar_events(request):
    # Recuperar las credenciales de la sesión
    credentials_data = request.session.get('credentials')
    if not credentials_data:
        return redirect('google_auth')

    credentials = Credentials(**credentials_data)

    # Usar las credenciales para acceder a Google Calendar API
    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(
        calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    return render(request, 'calendar.html', {'events': events})
