from flask import Flask, redirect, session, render_template, request
import secrets
import os
from dotenv import load_dotenv
from urllib.parse import urlencode ## ^^ dependencias principais
import requests
import sqlite3
app = Flask(__name__)
callback_url = 'http://127.0.0.1:5000/callback'
load_dotenv()
client_id = os.getenv('SST_CLIENT_ID')
app_key = os.getenv('FLASK_SECRET')
app.secret_key = app_key
secret = os.getenv('SST_SECRET')
DB = os.path.join(os.path.dirname(__file__), 'sst.db')

def init_db(location = DB):
    conn = sqlite3.connect(location)
    conn.execute('CREATE TABLE IF NOT EXISTS users (spotify_id TEXT PRIMARY KEY, name TEXT, refresh_token TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS plays (user_id TEXT, track TEXT, artist TEXT, duration_ms INTEGER, time_played TEXT, UNIQUE(user_id, time_played))')
    conn.commit()
    conn.close()
init_db()


def collect(spotify_id, access_token):
    response = requests.get(
        'https://api.spotify.com/v1/me/player/recently-played',
        headers={'Authorization': f"Bearer {access_token}"}, 
        params={'limit': 50}
    )
    if response.status_code != 200:
        print(f"Erro ao coletar dados do Spotify: {response.status_code} - {response.text}")
        return
    items = response.json()['items']
    conn = sqlite3.connect(DB)
    for item in items:
        track = item['track']
        conn.execute('INSERT OR IGNORE INTO plays (user_id, track, artist, duration_ms, time_played) VALUES (?, ?, ?, ?, ?)',
                     (spotify_id, track['name'], track['artists'][0]['name'], track['duration_ms'], item['played_at']))
    conn.commit()
    conn.close()
    

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
        'redirect_uri': callback_url,
        'state': session['state']
    }
    encoded = urlencode(parameters)
    return redirect(f'https://accounts.spotify.com/authorize?{encoded}')

@app.route('/callback')
def callback():
    state = request.args.get('state')
    code = request.args.get('code')
    error = request.args.get('error')
    if error:
        return redirect('/error')

    if not state:
        return redirect('/')
    if state != session.pop('state', None):
        return redirect('/')
    
    # login auth
    parametros = {
        'grant_type': 'authorization_code',  
        'code': code,                        
        'redirect_uri': callback_url         
    }

    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data=parametros,
        auth=(client_id, secret)
    )

    if response.status_code != 200:
        return response.text

  
    tokens = response.json()
    session['access_token'] = tokens['access_token']
    eu = requests.get(

        'https://api.spotify.com/v1/me',
        headers={'Authorization': f"Bearer {session['access_token']}"}
    )
    if eu.status_code != 200:
        return eu.text
    user = eu.json()
    session['spotify_id'] = user['id']
    name = user['display_name']
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (spotify_id, name, refresh_token) VALUES (?, ?, ?)', (user['id'], name, tokens['refresh_token']))
    conn.commit()
    conn.close()
    collect(user['id'], session['access_token'])
    return f"Olá, {name}! Você está logado com sucesso."

@app.route('/error')
def error():
    return "Login cancelado"


if __name__ == '__main__':
    app.run(debug=True)
