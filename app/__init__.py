from flask import Flask, render_template, request
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})

app.config.from_object('config')
from app import routes
