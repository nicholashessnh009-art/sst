from flask import Flask, redirect, session, render_template, request
import secrets
import os
from dotenv import load_dotenv
from urllib.parse import urlencode ## ^^ dependencias principais
import requests
app = Flask(__name__)
callback_url = 'http://127.0.0.1:5000/callback'
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
    session['refresh_token'] = tokens['refresh_token']


    eu = requests.get(

        'https://api.spotify.com/v1/me',
        headers={'Authorization': f"Bearer {session['access_token']}"}
    )
    if eu.status_code != 200:
        return eu.text
    user = eu.json()
    name = user['display_name']
    return f"Olá, {name}! Você está logado com sucesso."

@app.route('/error')
def error():
    return "Login cancelado"


if __name__ == '__main__':
    app.run(debug=True)
