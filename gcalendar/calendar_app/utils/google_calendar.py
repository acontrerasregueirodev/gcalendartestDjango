import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    # Comprobar si ya existen credenciales guardadas en 'token.pickle'
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas o están expiradas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Actualizar credenciales si están expiradas
        else:
            # Iniciar el flujo de autorización OAuth 2.0
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=56748)  # Este es el puerto que usas en tu script
            
        # Guardar las credenciales en 'token.pickle' para futuras ejecuciones
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def list_events():
    creds = get_credentials()
    try:
        service = build('calendar', 'v3', credentials=creds)
        events_result = service.events().list(
            calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Llamar a la función para listar eventos
list_events()
