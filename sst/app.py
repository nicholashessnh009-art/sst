from flask import Flask, redirect, session, request, jsonify
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
    
def getAccessToken(spotify_id):
    conn = sqlite3.connect(DB)
    row = conn.execute('SELECT refresh_token FROM users WHERE spotify_id = ?', (spotify_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    refresh_token = row[0]
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'refresh_token', 'refresh_token': refresh_token},
        auth=(client_id, secret)
    )
    if response.status_code != 200:
        print(f"Erro ao obter token de acesso: {response.status_code} - {response.text}")
        return None
    tokens = response.json()
    new_refresh = tokens.get('refresh_token')
    if new_refresh:
        conn = sqlite3.connect(DB)
        conn.execute('UPDATE users SET refresh_token = ? WHERE spotify_id = ?', (new_refresh, spotify_id))
        conn.commit()
        conn.close()
    return tokens['access_token']

def collect_all():
    conn = sqlite3.connect(DB)
    rows = conn.execute('SELECT spotify_id FROM users').fetchall()
    conn.close()
    for row in rows:
        spotify_id = row[0]
        access_token = getAccessToken(spotify_id)
        if access_token:
            collect(spotify_id, access_token)
        else:
            print(f' não foi possivel coletar dados de {spotify_id}.')

def top_tracks_count():
    conn = sqlite3.connect(DB)
    

@app.route('/')
def home():
    return app.send_static_file('home.html')

@app.route('/login')
def login():
    session['state'] = secrets.token_hex(16)

    parameters = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': 'user-read-recently-played user-top-read',
        'redirect_uri': callback_url,
        'state': session['state'],
        'show_dialog': 'true'
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
    collect_all()
    return redirect('/profile')

@app.route('/refresh')
def refresh():
    if not session.get('spotify_id'):
        return redirect('/login')
    collect_all()
    return redirect('/profile')

@app.route('/profile')
def profile():
    spotify_id = session.get('spotify_id')
    if not spotify_id:
        return redirect('/login')
    
    return app.send_static_file('profile.html')

@app.route('/leaderboard')
def leaderboard():
    return app.send_static_file('leaderboard.html')

@app.route('/api/leaderboard')
def api_leaderboard():
    conn = sqlite3.connect(DB)
    ranking = conn.execute('''
    SELECT users.spotify_id, users.name, ROUND(SUM(plays.duration_ms) / 60000.0, 1) AS minutes
    FROM plays JOIN users ON plays.user_id = users.spotify_id
    GROUP BY plays.user_id
    ORDER BY minutes DESC

''').fetchall()

    top_artists = conn.execute('''
    SELECT plays.artist, COUNT(*) AS times_played FROM plays
    GROUP BY plays.artist ORDER BY times_played DESC LIMIT 5 
''').fetchall()
    conn.close()
    
    return jsonify({
        'ranking': [{'id': row[0], 'name': row[1], 'minutes': row[2]} for row in ranking],
        'top_artists': [{'artist': row[0], 'times_played': row[1]} for row in top_artists],
        'me': {'name': session.get('spotify_id')}
    })

@app.route('/api/profile') ## to do list: adicionar counter de quantas vezes os top_tracks foram tocados.
def api_profile():
    spotify_id = session.get('spotify_id')
    if not spotify_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    token = getAccessToken(spotify_id)
    if not token:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    headers = {'Authorization': f"Bearer {token}"}
    top = {'limit': 5, 'time_range': 'short_term'}

    r_artists = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers, params=top)
    r_tracks = requests.get('https://api.spotify.com/v1/me/top/tracks', headers=headers, params=top)
    artists = r_artists.json().get('items') if r_artists.status_code == 200 else []
    spotify_top_tracks = r_tracks.json().get('items') if r_tracks.status_code == 200 else []

    conn = sqlite3.connect(DB)
    name = conn.execute('SELECT name FROM users WHERE spotify_id = ?', (spotify_id,)).fetchone()[0]
    total_ms = conn.execute('SELECT SUM(duration_ms) FROM plays WHERE user_id = ?', (spotify_id,)).fetchone()[0] or 0
    plays_count = conn.execute('SELECT COUNT(*) FROM plays WHERE user_id = ?', (spotify_id,)).fetchone()[0]
    conn.close()

    minutes = round(total_ms / 60000, 1)
    return jsonify({
        'name': name,
        'minutes': minutes,
        'plays_count': plays_count,
        'top_artists': [artist['name'] for artist in artists],
        'top_artist_image': [artist['images'][0]['url'] for artist in artists if artist['images']],
        'top_tracks': [{'track': track['name'], 'artist': track['artists'][0]['name']} for track in spotify_top_tracks]
       
    })  

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/error')
def error():
    return "Login cancelado"


if __name__ == '__main__':
    app.run(debug=True)
