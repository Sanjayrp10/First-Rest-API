from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, or_
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, default=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    seats = db.Column(db.String(250), nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "has_sockets": self.has_sockets,
            "has_toilet": self.has_toilet,
            "has_wifi": self.has_wifi,
            "can_take_calls": self.can_take_calls,
            "seats": self.seats,
            "coffee_price": self.coffee_price,
        }


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    random_cafe = db.session.execute(db.select(Cafe).order_by(db.sql.func.random()).limit(1)).scalar()
    return jsonify({"Cafe": random_cafe.to_dict()})


@app.route("/all_cafes")
def get_all_cafes():
    all_cafes = db.session.execute(select(Cafe)).scalars().all()
    return jsonify({"cafes": [cafe.to_dict() for cafe in all_cafes]})


@app.route("/search")
def search_cafe():
    query_location = request.args.get("location")
    query_name = request.args.get("name")
    cafe_in_location = db.session.execute(
        db.select(Cafe).where(or_(Cafe.name == query_location, Cafe.name == query_name)))
    all_cafes = cafe_in_location.scalars().all()
    if all_cafes:
        return jsonify({"cafes": [cafe.to_dict() for cafe in all_cafes]})
    else:
        return "<p>Sorry, Value Not Found.</p>"


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        query_id = int(request.args.get("id"))
        query_name = request.args.get("name")
        query_map_url = request.args.get("map_url")
        query_img_url = request.args.get("img_url")
        query_location = request.args.get("location")
        query_has_sockets = bool(request.args.get("has_sockets"))
        query_has_toilet = bool(request.args.get("has_toilet"))
        query_has_wifi = bool(request.args.get("has_wifi"))
        query_can_take_calls = bool(request.args.get("can_take_calls"))
        query_seats = int(request.args.get("seats"))
        query_coffee_price = request.args.get("coffee_price")
        db.session.execute(db.insert(Cafe).values(coffee_price=query_coffee_price, seats=query_seats,
                                                  can_take_calls=query_can_take_calls, has_wifi=query_has_wifi,
                                                  has_toilet=query_has_toilet, has_sockets=query_has_sockets,
                                                  img_url=query_img_url, map_url=query_map_url, id=query_id,
                                                  name=query_name, location=query_location))
        db.session.commit()
        return jsonify({"message": "Cafe inserted successfully."})
    else:
        return "<p>Sorry, Method Not Found.</p>"


@app.route("/update", methods=["PATCH"])
def update():
    if request.method == "PATCH":
        query_id = int(request.args.get("id"))
        parameter = request.args.get("parameter")
        parameter_value = request.args.get(parameter)
        update_data = {parameter: parameter_value}
        db.session.execute(db.update(Cafe).values(update_data).where(Cafe.id == query_id))
        db.session.commit()
        return jsonify({"message": "Cafe updated successfully."})
    else:
        return "<p>Sorry, Method Not Found.</p>"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
