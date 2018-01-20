from flask import Flask
from flask_restful import Api
from WOrderFlask.resources.order import Order

app = Flask(__name__)
api = Api(app)

api.add_resource()
