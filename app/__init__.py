from flask import Flask, render_template, request
from flask_cors import CORS
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)
CORS(app)

app.config.from_object('config')
from app import routes
