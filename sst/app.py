from flask import Flask, redirect, session, render_template
import secrets
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
app = Flask(__name__)
load_dotenv()
client_id = os.getenv('SST_CLIENT_ID')
app_key = os.getenv('FLASK_SECRET')
app.secret_key = app_key
secret = os.getenv('SST_SECRET')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    session['state'] = secrets.token_hex(16)
    parameters = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': 'user-read-recently-played user-top-read',
        'redirect_uri': 'http://127.0.0.1:5000/callback',
        'state': session['state']
    }
    encoded = urlencode(parameters)
    return redirect(f'https://accounts.spotify.com/authorize?{encoded}')
    










if __name__ == '__main__':
    app.run(debug=True)
