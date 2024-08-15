from sqlite3 import IntegrityError
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.auth.pass_utils import get_password_hash
from src.auth.utils import create_access_token, create_refresh_token
from src.auth.schemas import RoleEnum, UserCreate
from config.db import Base, get_db
from main import app
from src.auth.models import User
from src.contacts.models import Contact
from src.auth.models import Role

# Используем тестовую базу данных
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
    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)
    yield
    # Удаление всех таблиц
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_db):
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()  # Rollback any changes after each test
    finally:
        session.close()

@pytest.fixture(scope="function")
def user_password(faker):
    # Генерация пароля для использования в тестах
    return faker.password()

@pytest.fixture(scope="function")
def user_role(db_session):
    role = db_session.query(Role).filter_by(name=RoleEnum.USER.value).first()
    if not role:
        role = Role(name=RoleEnum.USER.value)
        db_session.add(role)
        db_session.commit()
    return role

@pytest.fixture(scope="function")
def test_user(db_session, faker, user_password, user_role):
    hashed_password = get_password_hash(user_password)
    new_user = User(
        username=faker.user_name(),
        email=faker.email(),
        is_active=True,
        hashed_password=hashed_password,
        role_id=user_role.id,
    )

    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)  # To get the ID from the database
    return new_user

@pytest.fixture(scope="function")
def override_get_db(db_session):
    def _get_db():
        with db_session as session:
            yield session

    app.dependency_overrides[get_db] = _get_db

    yield
    app.dependency_overrides.clear()

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
def test_user_contact(db_session, test_user, faker) -> Contact:
    contact = Contact(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        phone_number=faker.phone_number(),
        owner_id=test_user.id,
        birthday=faker.date_of_birth(),
        additional_info=faker.text(),  # Normally optional field with some content
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact
