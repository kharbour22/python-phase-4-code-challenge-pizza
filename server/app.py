#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class AllRestaurants(Resource):

    def get(self):
        restaurants = Restaurant.query.all()
        restaurants_list = [restaurant.to_dict(only=('id', 'address', 'name'))for restaurant in restaurants]
        return make_response(restaurants_list, 200)
api.add_resource(AllRestaurants, "/restaurants")

class RestaurantById(Resource):

    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:
            response_body = restaurant.to_dict(rules = ('-restaurant_pizzas.restaurant','-restaurant_pizzas.pizza.restaurant_pizzas' ))
            return make_response (response_body, 200)
        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return make_response(response_body, 404)
        
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response_body = {}
            return make_response(response_body, 204)
        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return make_response(response_body, 404)

api.add_resource(RestaurantById, "/restaurants/<int:id>")

class AllPizzas(Resource):
    def get(self):
        response_body = [pizza.to_dict(rules = ('-restaurant_pizzas',)) for pizza in Pizza.query.all()]
        return make_response(response_body, 200)
api.add_resource(AllPizzas, "/pizzas")

class AllRestaurantPizza(Resource):
    def post(self):
        try:
            new_pizza = RestaurantPizza(price = request.json.get('price'), pizza_id = request.json.get('pizza_id'), restaurant_id = request.json.get('restaurant_id'))
            db.session.add(new_pizza)
            db.session.commit()
            response_body = new_pizza.to_dict(rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas'))
            return make_response(response_body, 201)
        except:
            response_body= {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

api.add_resource(AllRestaurantPizza, "/restaurant_pizzas")

        

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
