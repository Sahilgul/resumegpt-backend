import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import verify_password, get_password_hash


from app.database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)



@pytest.fixture(scope="function")
def test_db():
    # Create tables before test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    # Rollback & drop tables after test
    db.rollback()
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_register_user(test_db):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword", "name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_user_duplicate_email(test_db):
    # Register a user first
    client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "testpassword", "name": "Test User"}
    )
    
    # Try to register with the same email
    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "testpassword2", "name": "Another User"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_user(test_db):
    # Register a user first
    client.post(
        "/auth/register",
        json={"email": "login_test@example.com", "password": "testpassword", "name": "Login Test"}
    )
    
    # Try to login
    response = client.post(
        "/auth/login",
        data={"username": "login_test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password(test_db):
    # Register a user first
    client.post(
        "/auth/register",
        json={"email": "wrong_pw@example.com", "password": "testpassword", "name": "Wrong Password Test"}
    )
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={"username": "wrong_pw@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)