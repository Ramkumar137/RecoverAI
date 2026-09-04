import pytest
from starlette.testclient import TestClient
from app.main import app
from app.database import SessionLocal, get_db


from app.utils.seed_data import seed_demo_cases


@pytest.fixture(scope="session", autouse=True)
def setup_test_demo_cases():
    session = SessionLocal()
    try:
        seed_demo_cases(session, reset=True)
        session.commit()
    finally:
        session.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
