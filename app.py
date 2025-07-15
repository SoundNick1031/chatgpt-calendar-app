from flask import Flask, request, jsonify
import os
import pickle
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
app = Flask(__name__)

def get_credentials():
    creds = None
    token_path = '/etc/secrets/token.pickle' # Secret File にアップしたパス

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    else:
        raise Exception("token.pickle が存在しません。ローカルで生成して Render に Secret File としてアップロードしてください。")

    return creds

@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.json
    summary = data.get('summary')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if not summary or not start_time or not end_time:
        return jsonify({'error': 'summary, start_time, end_time が必要です'}), 400

    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify({'message': 'Event created', 'id': created_event.get('id')}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
