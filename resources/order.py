from flask_restful import Resource, reqparse, fields, marshal_with
import enum


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
        'shortcode': fields.String,
        'description': fields.String,
        'display_name': fields.String,
        'price': fields.Float
    }

    def __init__(self,
                 shortcode,
                 description,
                 display_name,
                 price):
        self.shortcode = shortcode
        self.description = description
        self.display_name = display_name
        self.price = price


class WProductQuantity(object):
    """A tuple of a @WProduct and an amount of said products
    """
    marshal_fields = {
        'quantity': fields.Integer,
        'product': fields.Nested(WProduct.marshal_fields)
    }

    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity


class WOption(WProduct):
    """A @WProduct whose availablity can be enabled/disabled via a function.
    """
    marshal_fields = WProduct.marshal_fields.copy()
    marshal_fields.update({'enable_function_name': fields.String})

    def __init__(self, enable_function_name, *args, **kwargs):
        super(WOption, self).__init__(self, args, kwargs)
        self.enable_function_name = enable_function_name


class WToppingPlacement(enum.Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    WHOLE = 3


class WTopping(WOption):
    marshal_fields = WOption.marshal_fields.copy()
    marshal_fields.update({'flavor_factor': fields.Float})
    marshal_fields.update({'bake_factor': fields.Float})
    marshal_fields.update({'idx': fields.Integer})

    def __init__(self, idx, flavor_factor, bake_factor, *args, **kwargs):
        super(WTopping, self).__init__(self, args, kwargs)
        self.idx = idx
        self.flavor_factor = flavor_factor
        self.bake_factor = bake_factor


class WPlacedTopping(object):
    """A tuple of a @WTopping and a @WToppingPlacement
    """
    marshal_fields = {
        'topping': fields.Nested(WTopping.marshal_fields),
        'placement': fields.String
    }

    def __init__(self, placement, topping):
        self.placement = placement
        self.topping = topping


class WPizza(WProduct):
    marshal_fields = WProduct.marshal_fields.copy()
    marshal_fields.update({
        'toppings': fields.Nested(WPlacedTopping.marshal_fields)})
    marshal_fields.update({
        'crust_flavor': fields.Nested(WOption.marshal_fields)})
    marshal_fields.update({
        'dough': fields.Nested(WOption.marshal_fields)})
    marshal_fields.update({
        'cheese': fields.Nested(WOption.marshal_fields)})
    marshal_fields.update({
        'sauce': fields.Nested(WOption.marshal_fields)})


class WOrder(object):
    marshal_fields = {
        'o_id': fields.String,
        # TODO: smart polymorphic compatible way to get the right polymorphic
        # nested fields thingy
        'products': fields.List(fields.Nested(WProductQuantity.marshal_fields)),
        'status': fields.String,
        'client_data': fields.Nested(WClientData.marshal_fields)
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
        orders[order_id] = WOrder(order_id,
            [WProductQuantity(
                WProduct("z", "The best thing", "displaaaay nanme", 5), 5)],
                args['status'], "delivery", None, {})
        return orders[order_id]
