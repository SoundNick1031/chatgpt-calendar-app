from flask import Flask, request, jsonify
import datetime
import os.path
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
app = Flask(__name__)

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080, open_browser=True)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.json
    summary = data.get('summary')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'},
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify({'message': 'Event created', 'id': event.get('id')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

