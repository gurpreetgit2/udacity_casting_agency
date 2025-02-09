import os
import unittest
import json
from flask import Flask
from dotenv import load_dotenv
from .models import setup_db, db, Movie, Actor
from .api import create_app  # Import a factory function if available


class CastingAgencyTestCase(unittest.TestCase):
    """This class has the test cases for the Casting Agency API"""

    @classmethod
    def setUpClass(cls):
        """Load environment variables once for all tests."""
        load_dotenv(
            dotenv_path=os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../.env")
            )
        )

    def setUp(self):
        """Define test variables and initialize app with test database."""
        self.database_path = (
            f"{os.getenv('DATABASE_URL')}{os.getenv('TEST_DATABASE_NAME')}"
        )

        test_config = {"SQLALCHEMY_DATABASE_URI": self.database_path}

        self.app = create_app(test_config)  # Pass test_config here
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

        # Load tokens from environment
        self.producer_token = os.getenv("PRODUCER_TOKEN")
        self.director_token = os.getenv("DIRECTOR_TOKEN")
        self.assistant_token = os.getenv("ASSISTANT_TOKEN")

        # assert if tokens are available before running other test cases
        assert self.producer_token, "PRODUCER_TOKEN not found in .env"
        assert self.director_token, "DIRECTOR_TOKEN not found in .env"
        assert self.assistant_token, "ASSISTANT_TOKEN not found in .env"

        # sample data addition
        self.new_actor = {"name": "Johny Depp", "age": 60, "gender": "Male"}
        self.new_movie = {"title": "Matrix", "release_date": "2020-01-01"}

    def tearDown(self):
        """Clean up the database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Success and error tests for GET /actors
    def test_get_actors_success(self):
        actor = Actor(name="Test Actor", age=40, gender="Female")
        actor.insert()
        response = self.client.get(
            "/actors", headers={"Authorization": f"Bearer {self.assistant_token}"}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

    def test_get_actors_failure(self):
        response = self.client.get("/invalid_endpoint")
        self.assertEqual(response.status_code, 404)

    # Success and error tests for POST /actors
    def test_create_actor_success(self):
        response = self.client.post(
            "/actors",
            json=self.new_actor,
            headers={"Authorization": f"Bearer {self.director_token}"},
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

    def test_create_actor_failure(self):
        response = self.client.post(
            "/actors",
            json={},
            headers={"Authorization": f"Bearer {self.director_token}"},
        )
        self.assertEqual(response.status_code, 400)

    # Success and error tests for PATCH /actors
    def test_update_actor_success(self):
        actor = Actor(name="Test Actor", age=40, gender="Female")
        actor.insert()
        response = self.client.patch(
            f"/actors/{actor.id}",
            json={"age": 35},
            headers={"Authorization": f"Bearer {self.director_token}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_update_actor_failure(self):
        response = self.client.patch(
            "/actors/9999",
            json={"age": 35},
            headers={"Authorization": f"Bearer {self.director_token}"},
        )
        self.assertEqual(response.status_code, 404)

    # RBAC tests
    def test_assistant_cannot_add_actor(self):
        response = self.client.post(
            "/actors",
            json=self.new_actor,
            headers={"Authorization": f"Bearer {self.assistant_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_director_can_add_actor(self):
        response = self.client.post(
            "/actors",
            json=self.new_actor,
            headers={"Authorization": f"Bearer {self.director_token}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_producer_can_delete_movie(self):
        movie = Movie(title="Test Movie", release_date="2026-01-01")
        movie.insert()
        response = self.client.delete(
            f"/movies/{movie.id}",
            headers={"Authorization": f"Bearer {self.producer_token}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_director_cannot_delete_movie(self):
        movie = Movie(title="Test Movie", release_date="2026-01-01")
        movie.insert()
        response = self.client.delete(
            f"/movies/{movie.id}",
            headers={"Authorization": f"Bearer {self.director_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_director_delete_actor_success(self):
        """Test director successfully deleting an actor."""
        # Step 1: Create an actor
        actor = Actor(name="Test Actor", age=30, gender="Male")
        actor.insert()

        # Step 2: Delete the actor
        response = self.client.delete(
            f"/actors/{actor.id}",
            headers={
                "Authorization": f"Bearer {self.director_token}"
            },  # Assuming directors can delete actors
        )
        data = json.loads(response.data)

        # Step 3: Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

        # Step 4: Confirm the actor is actually deleted
        deleted_actor = Actor.query.get(actor.id)
        self.assertIsNone(deleted_actor)

    def test_assistant_cannot_delete_actor(self):
        """Test that an assistant cannot delete an actor."""
        # Step 1: Create an actor
        actor = Actor(name="Restricted Actor", age=35, gender="Non-binary")
        actor.insert()

        # Step 2: Attempt deletion as an assistant (should fail)
        response = self.client.delete(
            f"/actors/{actor.id}",
            headers={
                "Authorization": f"Bearer {self.assistant_token}"
            },  # Assistant trying to delete
        )
        data = json.loads(response.data)

        # Step 3: Validate response
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertFalse(data["success"])
        self.assertEqual(
            data["message"], "Permission not found."
        )  # Assuming this is your RBAC failure message

        # Step 4: Confirm the actor is still in the database
        actor_still_exists = Actor.query.get(actor.id)
        self.assertIsNotNone(actor_still_exists)


if __name__ == "__main__":
    unittest.main()
