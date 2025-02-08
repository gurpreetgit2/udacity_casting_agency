import os
import logging
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .models import db_drop_and_create_all, setup_db, Movie, Actor
from .auth.auth import AuthError, requires_auth

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(
    filename=os.path.join(log_dir, "execution.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    CORS(app)

    # Uncomment below line for first run to reset the database
    # db_drop_and_create_all()

    # ROUTES
    @app.route("/", methods=["GET"])
    def get_health():
        return jsonify({"success": True, "health": True})

    @app.route("/actors", methods=["GET"])
    @requires_auth("get:actors")
    def get_actors(jwt):
        actors = Actor.query.all()
        if not actors:
            abort(404, description="No actors found")
        return jsonify(
            {"success": True, "actors": [actor.format() for actor in actors]}
        )

    @app.route("/movies", methods=["GET"])
    @requires_auth("get:movies")
    def get_movies(jwt):
        movies = Movie.query.all()
        if not movies:
            abort(404, description="No movies found")
        return jsonify(
            {"success": True, "movies": [movie.format() for movie in movies]}
        )

    @app.route("/actors", methods=["POST"])
    @requires_auth("post:actors")
    def create_actor(jwt):
        body = request.get_json()
        if not body:
            abort(400, description="Bad request, no data provided")

        name = body.get("name", None)
        age = body.get("age", None)
        gender = body.get("gender", None)
        if not name or not age or not gender:
            abort(400, description="Missing required fields")

        new_actor = Actor(name=name, age=age, gender=gender)
        new_actor.insert()
        return jsonify({"success": True, "actor": new_actor.format()})

    @app.route("/movies", methods=["POST"])
    @requires_auth("post:movies")
    def create_movie(jwt):
        body = request.get_json()
        if not body:
            abort(400, description="Bad request, no data provided")

        title = body.get("title", None)
        release_date = body.get("release_date", None)
        if not title or not release_date:
            abort(400, description="Missing required fields")

        new_movie = Movie(title=title, release_date=release_date)
        new_movie.insert()
        return jsonify({"success": True, "movie": new_movie.format()})

    @app.route("/actors/<int:id>", methods=["PATCH"])
    @requires_auth("patch:actors")
    def update_actor(jwt, id):
        actor = Actor.query.get(id)
        if not actor:
            abort(404, description="Actor not found")

        body = request.get_json()
        if "name" in body:
            actor.name = body["name"]
        if "age" in body:
            actor.age = body["age"]
        if "gender" in body:
            actor.gender = body["gender"]
        actor.update()
        return jsonify({"success": True, "actor": actor.format()})

    @app.route("/movies/<int:id>", methods=["PATCH"])
    @requires_auth("patch:movies")
    def update_movie(jwt, id):
        movie = Movie.query.get(id)
        if not movie:
            abort(404, description="Movie not found")

        body = request.get_json()
        if "title" in body:
            movie.title = body["title"]
        if "release_date" in body:
            movie.release_date = body["release_date"]
        movie.update()
        return jsonify({"success": True, "movie": movie.format()})

    @app.route("/actors/<int:id>", methods=["DELETE"])
    @requires_auth("delete:actors")
    def delete_actor(jwt, id):
        actor = Actor.query.get(id)
        if not actor:
            abort(404, description="Actor not found")
        actor.delete()
        return jsonify({"success": True, "delete": id})

    @app.route("/movies/<int:id>", methods=["DELETE"])
    @requires_auth("delete:movies")
    def delete_movie(jwt, id):
        movie = Movie.query.get(id)
        if not movie:
            abort(404, description="Movie not found")
        movie.delete()
        return jsonify({"success": True, "delete": id})

    # Error Handling
    @app.errorhandler(AuthError)
    def auth_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": error.status_code,
                    "message": error.error["description"],
                }
            ),
            error.status_code,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Server Error: {error}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "Internal Server Error. Please try again later.",
                }
            ),
            500,
        )

    return app
