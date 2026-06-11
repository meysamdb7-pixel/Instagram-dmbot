from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get('IG_ACCESS_TOKEN', '')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'dmbot_verify_2024')

KEYWORDS = {
    "1": "سلام عزیزم! لینک محصولات: https://example.com",
    "قیمت": "قیمت از 150 تا 500 هزار تومانه. عدد 1 بفرست",
    "خرید": "برای خرید روی لینک بیو کلیک کن!",
    "سلام": "سلام! عدد 1 رو بفرست",
}

DEFAULT_MSG = "سلام! برای اطلاعات بیشتر عدد 1 رو بفرست"

@app.route('/')
def index():
    return 'DM Bot is running!'

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'status': 'ok'}), 200
    try:
        for entry in data.get('entry', []):
            for msg_event in entry.get('messaging', []):
                sender_id = msg_event.get('sender', {}).get('id')
                if not sender_id:
                    continue
                if 'message' in msg_event:
                    text = msg_event['message'].get('text', '').strip()
                    reply = KEYWORDS.get(text, DEFAULT_MSG)
                    send_message(sender_id, reply)
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({'status': 'ok'}), 200

def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': text},
        'access_token': ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    return r.json()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
