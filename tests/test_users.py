import pytest
from fastapi.testclient import TestClient
from src.main import app 
from src.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.schemas import UserSchemas

# Setup test DB (sqlite memory for example)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user(client):
    import uuid
    unique_email = f"testuser_{uuid.uuid4()}@test.com"
    unique_username = f"testuser_{uuid.uuid4().hex[:6]}"

    response = client.post("/users/register", json={
        "email": unique_email,
        "username": unique_username,
        "first_name": "Test",
        "last_name": "User",
        "password": "secret123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == unique_username
    assert data["email"] == unique_email


def test_register_duplicate_username():
    # Register first user
    client.post("/users/register", json={
        "username": "dupuser",
        "email": "dupuser1@example.com",
        "first_name": "Dup",
        "last_name": "User",
        "password": "secret123"
    })

    # Try to register with same username but different email
    response = client.post("/users/register", json={
        "username": "dupuser",
        "email": "dupuser2@example.com",
        "first_name": "Dup",
        "last_name": "User",
        "password": "secret123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken."


def test_register_duplicate_email():
    # Register first user
    client.post("/users/register", json={
        "username": "uniqueuser",
        "email": "dupemail@example.com",
        "first_name": "Dup",
        "last_name": "User",
        "password": "secret123"
    })

    # Try to register with different username but same email
    response = client.post("/users/register", json={
        "username": "uniqueuser2",
        "email": "dupemail@example.com",
        "first_name": "Dup",
        "last_name": "User",
        "password": "secret123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already taken."


def test_login_user():
    # Register user first
    client.post("/users/register", json={
        "username": "loginuser",
        "email": "loginuser@example.com",
        "first_name": "Login",
        "last_name": "User",
        "password": "secret123"
    })

    response = client.post("/users/login", json={
        "username": "loginuser",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_wrong_password():
    response = client.post("/users/login", json={
        "username": "loginuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_get_current_user():
    # Login first to get token
    login_resp = client.post("/users/login", json={
        "username": "loginuser",
        "password": "secret123"
    })
    token = login_resp.json()["access_token"]

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "loginuser"


def test_edit_user():
    login_resp = client.post("/users/login", json={
        "username": "loginuser",
        "password": "secret123"
    })
    token = login_resp.json()["access_token"]

    response = client.put(
        "/users/me",
        json={"first_name": "Updated", "last_name": "User"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"


def test_get_all_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(u["username"] == "loginuser" for u in data)


def test_search_users():
    response = client.get("/users/search?q=login")
    assert response.status_code == 200
    data = response.json()
    assert any("login" in u["username"] for u in data)


def test_get_user_by_id():
    # Get user id from known username
    response = client.get("/users/")
    users = response.json()
    user_id = next(u["id"] for u in users if u["username"] == "loginuser")

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id


def test_delete_user_unauthorized():
    # Attempt to delete another user without token
    response = client.delete("/users/1")
    assert response.status_code == 401


def test_delete_user_authorized():
    # Login first
    login_resp = client.post("/users/login", json={
        "username": "loginuser",
        "password": "secret123"
    })
    token = login_resp.json()["access_token"]

    # Delete self
    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Expect 204 No Content or 403 if user_id != 1 (adjust accordingly)
    assert response.status_code in [204, 403]


def test_get_my_posts():
    login_resp = client.post("/users/login", json={
        "username": "loginuser",
        "password": "secret123"
    })
    token = login_resp.json()["access_token"]

    response = client.get(
        "/users/1/posts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)