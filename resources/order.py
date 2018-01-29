from flask_restful import Resource, reqparse, fields, marshal_with


order_fields = {
    'o_id':         fields.String,
    'products':     fields.List,
    'status':       fields.String,
}


class WOrder(object):
    def __init__(self,
                 o_id,
                 products,
                 status,
                 service,
                 promise_time,
                 client_data):
        self.o_id = o_id
        self.products = products
        self.status = status
        self.service = service
        self.promise_time = promise_time
        self.client_data = client_data


orders = {
    "1": WOrder("1", [], "statu", "delivery", None, {})
}

parser = reqparse.RequestParser()
parser.add_argument("status")


class OrderById(Resource):
    def __init__(self, **kwargs):
        # self.db = kwargs['db']
        Resource.__init__(self)

    @marshal_with(order_fields)
    def get(self, o_id):
        return orders[o_id]


class OrderPost(Resource):
    @marshal_with(order_fields)
    def post(self):
        args = parser.parse_args()
        order_id = str(int(max(orders.keys())) + 1)
        orders[order_id] = WOrder(order_id, [],
                                  args['status'], "delivery", None, {})
        return orders[order_id]
