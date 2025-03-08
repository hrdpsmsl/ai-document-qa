import unittest
from services import UserService, DocumentService, QAService
from models import User, Document, Embedding
from extensions import db
from flask_jwt_extended import create_access_token
from app import create_app


class TestUserService(unittest.TestCase):
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

    def test_register_user(self):
        """Test user registration"""
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("User created successfully", response.get_json()["msg"])

    def test_login_user(self):
        """Test user login"""
        # First, register the user
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        self.client.post("/register", json=data)

        # Now login the user
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = self.client.post("/login", json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())

    def test_invalid_login(self):
        """Test invalid login"""
        data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.get_json()["msg"])


class TestDocumentService(unittest.TestCase):
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

    def test_upload_document(self):
        """Test document upload"""
        # Simulate login
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        self.client.post("/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        })
        login_response = self.client.post("/login", json=login_data)
        access_token = login_response.get_json()["access_token"]

        # Upload document
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "file": (open("sample.pdf", "rb"), "sample.pdf")
        }
        response = self.client.post("/documentupload", headers=headers, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Document uploaded successfully", response.get_json()["message"])

    def test_get_documents(self):
        """Test get all documents for the user"""
        # Simulate login and create a document
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        self.client.post("/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        })
        login_response = self.client.post("/login", json=login_data)
        access_token = login_response.get_json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.client.get("/getdocuments", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("documents", response.get_json())


class TestQAService(unittest.TestCase):
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

    def test_ask_question(self):
        """Test asking a question and getting an answer"""
        # Simulate login
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        self.client.post("/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        })
        login_response = self.client.post("/login", json=login_data)
        access_token = login_response.get_json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "query": "What is the capital of France?"
        }
        response = self.client.post("/askquestion", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.get_json())


if __name__ == '__main__':
    unittest.main()
