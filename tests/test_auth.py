import os
from unittest import TestCase
 
from app import app, db, bcrypt
from market.models import *

def create_user():
    password_hash = bcrypt.generate_password_hash("password").decode("utf-8")
    user = User(username="me1", password=password_hash)
    db.session.add(user)
    db.session.commit()


class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""

    def setUp(self):
        """Executed prior to each test."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        """ Test for user signing up"""
        post_data = {"username": "john10", "password": "messi10"}
        self.app.post("/signup", data=post_data)
        signedup_user = User.query.filter_by(username="mee").one()
        self.assertEqual(signedup_user.username, "mee")

    def test_signup_existing_user(self):
        """ Test when signing up a user, it should return an error message """
        create_user()
        post_data = {"username": "john10", "password": "messi10"}
        response = self.app.post("/signup", data=post_data)
        response_text = response.get_data(as_text=True)
        self.assertIn(
            "The username is taken. Please choose a different username.", response_text
        )

    def test_login_correct_password(self):
        """ Test for user logging in """
        create_user()
        post_data = {"username": "john10", "password": "messi10"}
        response = self.app.post("/login", data=post_data)

        response_text = response.get_data(as_text=True)
        self.assertNotIn("Log In", response_text)
        self.assertNotIn("Sign Up", response_text)

    def test_login_nonexistent_user(self):
        """ Test when logging in an user, it should return an error message """
        post_data = {"username": "john10", "password": "messi10"}
        response = self.app.post("/login", data=post_data)
        response_text = response.get_data(as_text=True)
        self.assertIn("Could not find a user with this username. Please try again.", response_text)

    def test_login_incorrect_password(self):
        """ Test when logging in a user with wrong password, it should return an error message """
        create_user()
        post_data = {"username": "john10", "password": "messi10"}
        response = self.app.post("/login", data=post_data)
        response_text = response.get_data(as_text=True)
        self.assertIn("Password does not match. Please try again.", response_text)

    def test_logout(self):
        """ Test for logout route """
        create_user()
        password_hash = bcrypt.generate_password_hash("messi10").decode("utf-8")
        post_data = {"username": "john10", "password": password_hash}
        self.app.post("/login", data=post_data)
        response = self.app.get("/logout", follow_redirects=True)

        response_text = response.get_data(as_text=True)
        self.assertIn("Log In", response_text)
        self.assertIn("Sign Up", response_text)