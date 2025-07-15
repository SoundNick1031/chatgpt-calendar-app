from flask import Flask, request, jsonify, make_response
import os
import json
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
app = Flask(__name__)

def get_credentials():
    token_base64 = os.getenv('TOKEN_JSON_BASE64')
    if not token_base64:
        raise Exception("環境変数 TOKEN_JSON_BASE64 が設定されていません")

    token_json_str = base64.b64decode(token_base64).decode('utf-8')
    token_data = json.loads(token_json_str)

    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    return creds

@app.route('/add_event', methods=['POST'])
def add_event():
    try:
        data = request.json
        print("受信データ:", data)

        summary = data.get('summary')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not summary or not start_time or not end_time:
            return make_response(
                jsonify({'error': 'summary, start_time, end_time が必要です'}),
                400,
                {"Content-Type": "application/json"}
            )

        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'},
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print("イベント作成結果:", created_event)

        return make_response(
            jsonify({'message': 'Event created', 'id': created_event.get('id')}),
            200,
            {"Content-Type": "application/json"}
        )

    except Exception as e:
        print("エラー:", str(e))
        return make_response(
            jsonify({'error': str(e)}),
            500,
            {"Content-Type": "application/json"}
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
