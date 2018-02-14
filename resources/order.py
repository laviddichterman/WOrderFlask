# -*- coding: utf-8 -*-

from flask_restful import Resource, reqparse
from flask_restful import fields, marshal_with, marshal
import enum


class WNestedField(fields.Nested):
    def __init__(self, *args, **kwargs):
        super(WNestedField, self).__init__(*args, **kwargs)

    def output(self, key, obj):
        value = fields.get_value(key if self.attribute is None
                                 else self.attribute, obj)
        if value is None:
            if self.allow_null:
                return None
            elif self.default is not None:
                return self.default

        if (hasattr(obj, "MarshalFields")):
            return marshal(value, obj.MarshalFields())
        else:
            return marshal(value, self.nested)


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

    def MarshalFields(self):
        return self.__class__.marshal_fields


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

    def MarshalFields(self):
        return self.__class__.marshal_fields


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

    def MarshalFields(self):
        return WProductQuantity.marshal_fields


class WOption(WProduct):
    """A @WProduct whose availablity can be enabled/disabled via a function.
    """
    marshal_fields = WProduct.marshal_fields.copy()
    marshal_fields.update({'enable_function_name': fields.String})

    def __init__(self, enable_function_name, *args, **kwargs):
        super(WOption, self).__init__(*args, **kwargs)
        self.enable_function_name = enable_function_name

    def MarshalFields(self):
        return WOption.marshal_fields


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
        super(WTopping, self).__init__(*args, **kwargs)
        self.idx = idx
        self.flavor_factor = flavor_factor
        self.bake_factor = bake_factor

    def MarshalFields(self):
        return WTopping.marshal_fields


class WToppings(enum.Enum):
    pepp = WTopping(0, 1, 1, "always_enable", "pepp", "Pepperoni", "Pepperoni", 2)
    spin = WTopping(1, 1, 1, "always_enable", "spin", "Wilted Spinach", "Wilted Spinach", 2)
    jala = WTopping(2, 1, 1, "always_enable", "jala", u"Fresh Jalapeño", u"Fresh Jalapeño", 2)
    mush = WTopping(3, 1, 1, "always_enable", "mush", "Mushroom", "Mushroom", 2)
    castel = WTopping(4, 1, 1, "always_enable", "castel", "Castelvetrano Olive", "Castelvetrano Olive", 2)
    kala = WTopping(5, 1, 1, "always_enable", "kala", "Kalamata Olive", "Kalamata Olive", 2)
    ro = WTopping(6, 1, 1, "always_enable", "ro", "Raw Red Onion", "Raw Red Onion", 2)
    co = WTopping(7, 1, 1, "always_enable", "co", "Caramelized Onion", "Caramelized Onion", 2)
    shp = WTopping(8, 1, 1, "always_enable", "shp", "Sweet Hot Pepper", "Sweet Hot Pepper", 2)
    gbp = WTopping(9, 1, 1, "always_enable", "gbp", "Green Bell Pepper", "Green Bell Pepper", 2)
    rbp = WTopping(10, 1, 1, "always_enable", "rbp", "Roasted Red Bell Pepper", "Roasted Red Bell Pepper", 2)
    pine = WTopping(11, 1, 1, "always_enable", "pine", "Pineapple", "Pineapple", 2)
    chx = WTopping(12, 1, 1, "disable_on_pork_sausage", "chx", "Rosemary Chicken Sausage", "Rosemary Chicken Sausage", 2)
    sausage = WTopping(13, 1, 1, "disable_on_chx", "sausage", "House Sausage (Pork)", "House Sausage", 2)
    mb = WTopping(14, 1, 2, "disable_on_gf", "mb", "Meatball", "Meatball", 4)
    brussels = WTopping(15, 1, 1, "disable_on_red", "brussels", "Brussels Sprout", "Brussels Sprout", 2)
    bacon = WTopping(16, 1, 1, "always_enable", "bacon", "Candied Bacon", "Candied Bacon", 2)
    bleu = WTopping(17, 1, 1, "always_enable", "bleu", "Bleu Cheese", "Bleu", 2)
    giard = WTopping(18, 1, 1, "always_enable", "giard", "Hot Giardiniera", "Hot Giardiniera", 2)

    @staticmethod
    def MarshalFields():
        return {"value": fields.Nested(WTopping.marshal_fields),
                "id": fields.String(attribute="name")}


class WPlacedTopping(object):
    """A tuple of a @WTopping and a @WToppingPlacement
    """
    marshal_fields = {
        'topping': fields.Nested(WToppings.MarshalFields()),
        'placement': fields.String
    }

    def __init__(self, placement, topping):
        self.placement = placement
        self.topping = topping

    def MarshalFields(self):
        return WPlacedTopping.marshal_fields


class WPizza(WProduct):
    @staticmethod
    def compute_price(pizza):
        val = 19
        base_prices = map(lambda x: x.value.price, [pizza.crust_flavor, pizza.dough, pizza.cheese, pizza.sauce])
        val += reduce(lambda x, y: x + y, base_prices)
        toppings_prices = map(lambda x:
                              x.topping.price if x.placement != WToppingPlacement.NONE
                              else 0,
                              pizza.toppings)
        val += reduce(lambda x, y: x + y, toppings_prices)
        return v

    @staticmethod
    def build_custom_shortcode(pizza):
        shortcode_builder = []
    #     if (pizza.crust.shortname === crusts.regular.shortname && pizza.sauce.shortname === "red") {
    #   shortcode_builder = "z";
    # }
    # if (pizza.crust.dough == crust_doughs.gf) {
    #   shortcode_builder = "k";
    # }
    # if (pizza.crust.flavor == crust_flavors.garlic) {
    #   shortcode_builder = shortcode_builder + "g";
    # }
    # if (pizza.sauce.shortname == "white") {
    #   shortcode_builder = shortcode_builder + "w";
    # }
    # return shortcode_builder;
    marshal_fields = WProduct.marshal_fields.copy()
    marshal_fields.update({
        'toppings': fields.Nested(WPlacedTopping.marshal_fields)})
    marshal_fields.update({
        'crust_flavor': fields.Nested(WOption.marshal_fields, attribute="crust_flavor.value")})
    marshal_fields.update({
        'dough': fields.Nested(WOption.marshal_fields, attribute="dough.value")})
    marshal_fields.update({
        'cheese': fields.Nested(WOption.marshal_fields, attribute="cheese.value")})
    marshal_fields.update({
        'sauce': fields.Nested(WOption.marshal_fields, attribute="sauce.value")})

    def __init__(self, toppings, crust_flavor, dough, cheese, sauce, *args, **kwargs):
        super(WPizza, self).__init__(*args, **kwargs)
        self.toppings = toppings
        self.crust_flavor = crust_flavor
        self.dough = dough
        self.cheese = cheese
        self.sauce = sauce

    def MarshalFields(self):
        return WPizza.marshal_fields


class WOrder(object):
    marshal_fields = {
        'o_id': fields.String,
        # TODO: smart polymorphic compatible way to get the right polymorphic
        # nested fields thingy
        'products': fields.List(WNestedField(WProductQuantity.marshal_fields)),
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

    def MarshalFields(self):
        return WOrder.marshal_fields




class WCrustDoughOptions(enum.Enum):
    brioche = WOption("always_enable", "brioche", "Regular", "Regular", 0)
    gf = WOption("disable_on_meatball", "gf", "Gluten Free Dough", "Gluten Free Dough", 5)


class WCrustFlavorOptions(enum.Enum):
    plain = WOption("always_enable", "plain", "Regular", "Regular", 0)
    garlic = WOption("always_enable", "garlic", "Roasted Garlic Crust", "Roasted Garlic Crust", 2)


class WCheeseOptions(enum.Enum):
    mozz = WOption("always_enable", "mozz", "Mozzarella Cheese", "Mozzarella Cheese", 0)
    ex_mozz = WOption("always_enable", "ex_mozz", "Extra Mozzarella Cheese", "Extra Mozzarella Cheese", 2)


class WSauceOptions(enum.Enum):
    red = WOption("disable_on_brussels", "red", "Red Sauce", "Red Sauce", 0)
    white = WOption("always_enable", "white", "White Sauce", "White Sauce", 2)


WCP_PIZZAS = {
    "omnivore": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.pepp),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.sausage),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.co),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.spin),
        ],
        WCrustFlavorOptions.garlic,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "O",
        "", # description
        "Omnivore",
        29.00
    ),
    "four_pepper": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.rbp),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.gbp),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.shp),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.jala)
        ],
        WCrustFlavorOptions.garlic,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "F",
        "", # description
        "4 Pepper",
        29.00
    ),
    "veggie": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.rbp),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.co),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.mush),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.spin)
        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "V",
        "", # description
        "Veggie",
        27.00
    ),
    "classic": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.sausage),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.rbp),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.co),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.mush),

        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "C",
        "", # description
        "Classic",
        27.00
    ),
    "popeye": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.bleu),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.kala),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.mush),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.spin),

        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "P",
        "", # description
        "Popeye",
        27.00
    ),
    "sweet_pete": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.giard),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.bacon),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.sausage),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.pine),
        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "S",
        "", # description
        "Sweet Pete",
        27.00
    ),
    "hot_island": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.sausage),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.pine),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.jala),
        ],
        WCrustFlavorOptions.garlic,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "H",
        "", # description
        "Hot Island",
        27.00
    ),
    "meatza": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.bacon),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.sausage),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.pepp),
        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "M",
        "", # description
        "Meatza",
        25.00
    ),
    "tuscany_raider": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.chx),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.shp),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.spin)
        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.white,
        "T",
        "", # description
        "Tuscany Raider",
        27.00
    ),
    "brussels_snout": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.bacon),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.brussels),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.co)
        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.white,
        "R",
        "", # description
        "Brussels Snout",
        27.00
    ),
    "blue_pig": WPizza(
        [
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.bleu),
            WPlacedTopping(WToppingPlacement.WHOLE, WToppings.bacon)
        ],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "B",
        "", # description
        "Blue Pig",
        23.00
    ),
    "byo": WPizza(
        [],
        WCrustFlavorOptions.plain,
        WCrustDoughOptions.brioche,
        WCheeseOptions.mozz,
        WSauceOptions.red,
        "z",
        "", # description
        "Build-Your-Own",
        19.00
    )
}

orders = {
    "1": WOrder("1", [], "statu", "delivery", None, {})
}

parser = reqparse.RequestParser()
parser.add_argument("status")


class MenuList(Resource):
    def __init__(self, **kwargs):
        # self.db = kwargs['db']
        Resource.__init__(self)

    @marshal_with({
        "pizza": fields.List(fields.Nested(WPizza.marshal_fields)),
        "salad": fields.List(fields.Nested(WProduct.marshal_fields))
    })
    def get(self):
        print WCP_PIZZAS.values()[0].cheese.value
        return {
            "pizza": WCP_PIZZAS.values(),
            "salad": []
              }


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
                WCP_PIZZAS["sweet_pete"], 5)],
                args['status'], "delivery", None, {})
        return orders[order_id]
