import unittest
from app import create_app
from extensions import db


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory database
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """Tear down after each test"""
        db.session.remove()
        db.drop_all()

    def test_register_route(self):
        """Test register route"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword"
        }
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("User created successfully", response.get_json()["msg"])

    def test_login_route(self):
        """Test login route"""
        data = {
            "email": "newuser@example.com",
            "password": "newpassword"
        }
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())

    def test_protected_route(self):
        """Test protected route with JWT"""
        login_data = {
            "email": "newuser@example.com",
            "password": "newpassword"
        }
        self.client.post("/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword"
        })
        login_response = self.client.post("/login", json=login_data)
        access_token = login_response.get_json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.client.get("/protected", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("logged_in_as", response.get_json())

if __name__ == "__main__":
    unittest.main()
