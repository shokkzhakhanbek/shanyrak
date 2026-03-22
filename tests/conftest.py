import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# In-memory SQLite для тестов
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Тестовые данные ─────────────────────────────────

USER_DATA = {
    "username": "test@gmail.com",
    "phone": "+7 700 698 5025",
    "password": "12345678",
    "name": "Далида Е.",
    "city": "Алматы",
}

USER_DATA_2 = {
    "username": "second@gmail.com",
    "phone": "+7 701 111 2222",
    "password": "password2",
    "name": "Арман К.",
    "city": "Астана",
}

SHANYRAK_DATA = {
    "type": "rent",
    "price": 150000,
    "address": "Астана, ул. Нажимеденова, 16",
    "area": 46.5,
    "rooms_count": 2,
    "description": "Продается 1.5 комнатная квартира.",
}


# ─── Хелперы ─────────────────────────────────────────

def register_user(client, data=None):
    data = data or USER_DATA
    resp = client.post("/auth/users/", json=data)
    assert resp.status_code == 200


def login_user(client, username=None, password=None):
    username = username or USER_DATA["username"]
    password = password or USER_DATA["password"]
    resp = client.post(
        "/auth/users/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def create_shanyrak(client, token, data=None):
    data = data or SHANYRAK_DATA
    resp = client.post("/shanyraks/", json=data, headers=auth_header(token))
    assert resp.status_code == 200
    return resp.json()["id"]