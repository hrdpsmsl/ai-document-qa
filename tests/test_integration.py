import unittest
from app import create_app  # Adjust based on your project structure
from extensions import db  # Ensure db is imported from your extensions or where it's defined

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory database
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Create a new app context for the database setup
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_workflow(self):
        """Test full user workflow from registration to QA"""
        # Register the user
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 201)

        # Login the user
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        login_response = self.client.post("/login", json=login_data)
        access_token = login_response.get_json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        # Upload a document
        data = {
            "file": (open("sample.pdf", "rb"), "sample.pdf")
        }
        response = self.client.post("/documentupload", headers=headers, data=data)
        self.assertEqual(response.status_code, 201)

        # Ask a question
        question_data = {
            "query": "What is the capital of France?"
        }
        response = self.client.post("/askquestion", json=question_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.get_json())

if __name__ == "__main__":
    unittest.main()
