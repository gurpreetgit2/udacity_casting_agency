from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables from the root-level .env file
load_dotenv(
    dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
)

database_path = f"{os.getenv('DATABASE_URL')}{os.getenv('DATABASE_NAME')}"

db = SQLAlchemy()


def db_drop_and_create_all():
    """Drops the database tables and recreates them."""
    db.drop_all()
    db.create_all()


def setup_db(app, database_path=database_path):
    """Binds a Flask application and SQLAlchemy service."""
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


# Actor Model
class Actor(db.Model):
    __tablename__ = "actors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)

    def format(self):
        """Returns a formatted JSON representation of an actor."""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
        }

    def insert(self):
        """Inserts a new actor into the database."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Updates an existing actor in the database."""
        db.session.commit()

    def delete(self):
        """Deletes an actor from the database."""
        db.session.delete(self)
        db.session.commit()


# Movie Model
class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date, nullable=False)

    def format(self):
        """Returns a formatted JSON representation of a movie."""
        return {
            "id": self.id,
            "title": self.title,
            "release_date": self.release_date.strftime("%Y-%m-%d"),
        }

    def insert(self):
        """Inserts a new movie into the database."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Updates an existing movie in the database."""
        db.session.commit()

    def delete(self):
        """Deletes a movie from the database."""
        db.session.delete(self)
        db.session.commit()
