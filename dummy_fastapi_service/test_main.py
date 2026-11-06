import unittest
from fastapi.testclient import TestClient
from .main import app
from .app.services.service import user_service
from .app.models.schemas import User

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Reset users to default state for each test
        user_service.users = [
            User(
                id=1,
                name="Alice Smith",
                email="alice@example.com",
                habits=["swim", "read"],
            ),
            User(id=2, name="Bob Jones", email="bob@example.com", habits=["sing"]),
            User(
                id=3,
                name="Charlie Brown",
                email="charlie@example.com",
                habits=["football"],
            ),
        ]
        user_service.current_id = 4

    def test_create_user(self):
        response = self.client.post(
            "/users",
            json={"name": "John Doe", "email": "john@example.com"}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["email"], "john@example.com")
        self.assertEqual(data["id"], 4)

    def test_get_users(self):
        # Starts with 3 default users
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_get_user(self):
        response = self.client.get("/users/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Alice Smith")

    def test_update_user(self):
        response = self.client.put(
            "/users/1",
            json={"name": "Alice Doe"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Alice Doe")
        self.assertEqual(response.json()["email"], "alice@example.com")

    def test_delete_user(self):
        response = self.client.delete("/users/1")
        self.assertEqual(response.status_code, 204)
        response = self.client.get("/users/1")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
