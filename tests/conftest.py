from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.auth.utils import create_access_token, create_refresh_token
from src.auth.pass_utils import get_password_hash
from src.auth.schemas import RoleEnum
from config.db import Base, get_db
from main import app
from src.auth.models import User, Role
from src.contacts.models import Contact

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_db):
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback() 
    finally:
        session.close()

@pytest.fixture(scope="function")
def user_password():
    return "test_password"

@pytest.fixture(scope="function")
def user_role(db_session):
    role = db_session.query(Role).filter_by(name=RoleEnum.USER.value).first()
    if not role:
        role = Role(name=RoleEnum.USER.value)
        db_session.add(role)
        db_session.commit()
    return role

@pytest.fixture(scope="function")
def test_user(db_session, user_password, user_role):
    hashed_password = get_password_hash(user_password)
    new_user = User(
        username="test_user",
        email="test_user@example.com",
        is_active=True,
        hashed_password=hashed_password,
        role_id=user_role.id,
    )

    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user) 
    return new_user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    refresh_token = create_refresh_token(data={"sub": test_user.username})
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Refresh-Token": refresh_token,
        "Content-Type": "application/json",
    }
    return headers

@pytest.fixture(scope="function")
def override_get_db(db_session):
    def _get_db():
        with db_session as session:
            yield session

    app.dependency_overrides[get_db] = _get_db

    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user_contact(db_session, test_user):
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="123456789",
    )
    contact.user_id = test_user.id
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact) 
    return contact