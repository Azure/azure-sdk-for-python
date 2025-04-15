# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for

from azure.projects import AzureApp
from azure.data.tables import TableClient, UpdateMode

from models import Restaurant, Review


app = Flask(__name__, template_folder="templates", static_folder="static")


class RestaurantReviewApp(AzureApp):
    restaurants: TableClient
    reviews: TableClient


azproject = RestaurantReviewApp.load(
    attr_map={"restaurants": "restaurant_data", "reviews": "review_data"},
)


@app.route("/", methods=["GET"])
def index():
    restaurants = [Restaurant(**e) for e in azproject.restaurants.list_entities()]
    return render_template("index.html", restaurants=restaurants)


@app.route("/<id>", methods=["GET"])
def details(id):
    restaurant = next(
        azproject.restaurants.query_entities("PartitionKey eq @partition", parameters={"partition": id}), None
    )
    if not restaurant:
        return (
            '<h1>404</h1><p>Restaurant not found!</p><img src="https://httpcats.com/404.jpg" alt="cat in box" width=400>',
            404,
        )
    reviews = [Review(**e) for e in azproject.reviews.query_entities("RowKey eq @row", parameters={"row": id})]
    return render_template("details.html", restaurant=Restaurant(**restaurant), reviews=reviews)


@app.route("/create", methods=["GET"])
def create_restaurant():
    return render_template("create_restaurant.html")


@app.route("/add", methods=["POST"])
def add_restaurant():
    name = request.values.get("restaurant_name")
    street_address = request.values.get("street_address")
    description = request.values.get("description")
    if not name or not street_address:
        error = "You must include a restaurant name and address."
        return render_template("create_restaurant.html", error=error)
    else:
        restaurant = Restaurant(name=name, street_address=street_address, description=description)
        azproject.restaurants.upsert_entity(restaurant.model_dump(by_alias=True), mode=UpdateMode.REPLACE)
    return redirect(url_for("details", id=restaurant.id))


@app.route("/review/<id>", methods=["POST"])
def add_review(id):
    user_name = request.values.get("user_name")
    rating = request.values.get("rating")
    review_text = request.values.get("review_text")

    review = Review(
        restaurant=id, user_name=user_name, rating=int(rating), review_text=review_text, review_date=datetime.now()
    )
    azproject.reviews.upsert_entity(review.model_dump(by_alias=True))
    return redirect(url_for("details", id=id))


@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = azproject.reviews.query_entities("RowKey eq @row", parameters={"row": id})
        ratings = []
        review_count = 0
        for review in reviews:
            ratings += [review["rating"]]
            review_count += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {"avg_rating": avg_rating, "review_count": review_count, "stars_percent": stars_percent}

    return dict(star_rating=star_rating)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


if __name__ == "__main__":
    app.run()
