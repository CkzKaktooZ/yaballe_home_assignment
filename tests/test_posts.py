import pytest
from fastapi.testclient import TestClient
from src.main import app  # adjust import to your FastAPI app
from src.database import get_db, Base, engine, SessionLocal
from sqlalchemy.orm import Session
from src.models import User, Post

client = TestClient(app)

# Use a fixture for db session (isolated for tests)
@pytest.fixture(scope="module")
def db():
    # create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    # drop tables after tests
    Base.metadata.drop_all(bind=engine)

# Helper to create and login user, return token
def create_and_login_user(username: str, email: str, password: str) -> str:
    client.post("/users/register", json={
        "username": username,
        "email": email,
        "first_name": "Test",
        "last_name": "User",
        "password": password
    })
    response = client.post("/users/login", json={
        "username": username,
        "password": password
    })
    return response.json()["access_token"]

@pytest.fixture
def auth_token():
    return create_and_login_user("testuser", "testuser@example.com", "secret123")

@pytest.fixture
def another_auth_token():
    return create_and_login_user("otheruser", "otheruser@example.com", "secret123")

def test_create_post(client, auth_token):
    response = client.post(
        "/posts/",
        json={"title": "My Test Post", "content": "This is a test content."},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Test Post"
    assert data["content"] == "This is a test content."
    assert "id" in data

def test_get_all_posts(client, auth_token):
    response = client.get("/posts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_posts(client, auth_token):
    response = client.get("/posts/search?q=Test")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    # optionally check if query matches in title or content

def test_get_post_by_id(client, auth_token):
    # create post first
    create_resp = client.post(
        "/posts/",
        json={"title": "Unique Post", "content": "Searchable content"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    post_id = create_resp.json()["id"]
    
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id

def test_get_post_by_invalid_id(client):
    response = client.get("/posts/99999999")  # unlikely to exist
    assert response.status_code == 404

def test_edit_post_by_id(client, auth_token, another_auth_token):
    # create post by testuser
    create_resp = client.post(
        "/posts/",
        json={"title": "Edit Me", "content": "Before edit"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    post_id = create_resp.json()["id"]

    # unauthorized user tries to edit
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "Hacked Title", "content": "Hacked content"},
        headers={"Authorization": f"Bearer {another_auth_token}"}
    )
    assert response.status_code == 403

    # authorized user edits post
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "Edited Title", "content": "Edited content"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Edited Title"
    assert data["content"] == "Edited content"

def test_delete_post(client, auth_token, another_auth_token):
    # create post by testuser
    create_resp = client.post(
        "/posts/",
        json={"title": "Delete Me", "content": "Will be deleted"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    post_id = create_resp.json()["id"]

    # unauthorized delete attempt
    response = client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {another_auth_token}"}
    )
    assert response.status_code == 403

    # authorized delete
    response = client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

    # confirm deletion
    get_resp = client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 404

def test_get_post_votes(client, auth_token):
    # create post first
    create_resp = client.post(
        "/posts/",
        json={"title": "Vote Post", "content": "Vote here"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    post_id = create_resp.json()["id"]

    response = client.get(f"/posts/{post_id}/votes")
    assert response.status_code == 200
    data = response.json()
    assert "upvotes" in data
    assert "downvotes" in data

def test_vote_on_post(client, auth_token, another_auth_token):
    # create post
    create_resp = client.post(
        "/posts/",
        json={"title": "Voting Post", "content": "Vote on me"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    post_id = create_resp.json()["id"]

    # upvote post as another user
    response = client.post(
        f"/posts/{post_id}/vote?vote=upvote",
        headers={"Authorization": f"Bearer {another_auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "upvotes" in data

    # downvote post as original user
    response = client.post(
        f"/posts/{post_id}/vote?vote=downvote",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "downvotes" in data
