import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
import app.main as main_module

TEST_DATABASE_URL = "sqlite:///./test_certificates.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Background processing uses the same test database.
    original_session_local = main_module.SessionLocal
    main_module.SessionLocal = TestingSessionLocal
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    main_module.SessionLocal = original_session_local
    Base.metadata.drop_all(bind=engine)
