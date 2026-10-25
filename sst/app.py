from flask import Flask, redirect, session
import secrets
import os
from dotenv import load_dotenv
app = Flask(__name__)
@app.route('/')
def home():
    return "Hello, World!"
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

load_dotenv()
client_id = os.getenv('SST_CLIENT_ID')
app_key = os.getenv('FLASK_SECRET')
secret = os.getenv('SST_SECRET')
