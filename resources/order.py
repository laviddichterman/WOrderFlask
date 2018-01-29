from flask_restful import Resource, reqparse, fields, marshal_with


class WClientData(object):
    """Client metadata used for logging
    """
    marshal_fields = {
        'load_time':    fields.DateTime,
        'submit_time':  fields.DateTime,
        'time_selection_time':    fields.DateTime,
        'user_agent':    fields.String
    }

    def __init__(self,
                 load_time,
                 submit_time,
                 time_selection_time,
                 user_agent):
        self.load_time = load_time
        self.submit_time = submit_time
        self.time_selection_time = time_selection_time
        self.user_agent = user_agent


class WProduct(object):
    """A Product: a good or a service
    """
    marshal_fields = {
    }


class WOrder(object):
    marshal_fields = {
        'o_id':         fields.String,
        'products':     fields.List(fields.String),
        'status':       fields.String,
        'client_data':  fields.Nested(WClientData.marshal_fields)
    }

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

    @marshal_with(WOrder.marshal_fields)
    def get(self, o_id):
        return orders[o_id]


class OrderPost(Resource):
    @marshal_with(WOrder.marshal_fields)
    def post(self):
        args = parser.parse_args()
        order_id = str(int(max(orders.keys())) + 1)
        orders[order_id] = WOrder(order_id, [],
                                  args['status'], "delivery", None, {})
        return orders[order_id]
