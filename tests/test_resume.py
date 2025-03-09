import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
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


@pytest.fixture
def auth_token(test_db):
    # Register a user
    client.post(
        "/auth/register",
        json={"email": "resume_test@example.com", "password": "testpassword", "name": "Resume Test"}
    )
    
    # Login and get token
    response = client.post(
        "/auth/login",
        data={"username": "resume_test@example.com", "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_upload_resume(test_db, auth_token):
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - Senior Developer at Tech Co (2018-2022)
    - Developer at Software Inc (2015-2018)
    
    Skills:
    - Python, JavaScript, React, FastAPI
    - Agile methodologies, Team leadership
    """
    
    sample_job = """
    We're looking for a Software Engineer with experience in:
    - Python and JavaScript
    - React and Node.js
    - Database design (SQL, NoSQL)
    - Team collaboration
    """
    
    response = client.post(
        "/resume/analyze",
        json={
            "resume_text": sample_resume,
            "job_description": sample_job
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "matched_tech_skills" in data
    assert "matched_soft_skills" in data
    assert "missing_tech_skills" in data
    assert "missing_soft_skills" in data
    assert "suggestions" in data
    
    # Check specific skills
    assert "Python" in [skill["name"] for skill in data["matched_tech_skills"]]
    assert "JavaScript" in [skill["name"] for skill in data["matched_tech_skills"]]
    assert "React" in [skill["name"] for skill in data["matched_tech_skills"]]
    assert "Node.js" in [skill["name"] for skill in data["missing_tech_skills"]]
    assert "Database design" in [skill["name"] for skill in data["missing_tech_skills"]]

def test_upload_resume_file(test_db, auth_token):
    sample_job = """
    We're looking for a Software Engineer with experience in:
    - Python and JavaScript
    - React and Node.js
    - Database design (SQL, NoSQL)
    - Team collaboration
    """
    
    # Create a mock PDF file
    mock_file = io.BytesIO(b"Mock PDF content with Python, JavaScript skills")
    
    response = client.post(
        "/resume/upload",
        files={"resume_file": ("resume.pdf", mock_file, "application/pdf")},
        data={"job_description": sample_job},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "matched_tech_skills" in data
    assert "matched_soft_skills" in data
    assert "missing_tech_skills" in data
    assert "missing_soft_skills" in data
    assert "suggestions" in data

def test_get_user_analysis_history(test_db, auth_token):
    # First upload a resume to create history
    sample_resume = "Sample resume with Python skills"
    sample_job = "Job description requiring Python and JavaScript"
    
    client.post(
        "/resume/analyze",
        json={
            "resume_text": sample_resume,
            "job_description": sample_job
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get analysis history
    response = client.get(
        "/resume/history",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "created_at" in data[0]