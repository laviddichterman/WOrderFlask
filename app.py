from flask import Flask
from flask_restful import Api
from resources.order import OrderById, OrderPost, MenuList

app = Flask(__name__)
api = Api(app)

orders = {}

api.add_resource(OrderById, '/order/<string:o_id>')
api.add_resource(OrderPost, '/order')
api.add_resource(MenuList, '/menu')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
