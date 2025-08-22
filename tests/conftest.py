import pytest
from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app("TestConfig")
    ctx = app.app_context()
    ctx.push()
    
    _db.create_all()
    
    yield app
    
    _db.session.remove()
    _db.drop_all()
    _db.engine.dispose()
    ctx.pop()


@pytest.fixture
def db(app):
    _db.session.rollback()
    
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()
    
    yield _db
    
    _db.session.rollback()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client, db):
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    # Register a test user
    register_resp = client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "secret"
    })
    
    # Check if registration was successful
    if register_resp.status_code != 201:
        raise Exception(f"Registration failed with status {register_resp.status_code}: {register_resp.get_json()}")
    
    # Login to get the token
    login_resp = client.post("/auth/login", json={
        "username": username,
        "password": "secret"
    })
    
    # Check if login was successful
    if login_resp.status_code != 200:
        raise Exception(f"Login failed: {login_resp.get_json()}")
    
    login_data = login_resp.get_json()
    token = login_data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True, scope="session")
def silence_limiter_warnings():
    import warnings
    warnings.filterwarnings(
        "ignore",
        message="Using the in-memory storage for tracking rate limits.*",
        category=UserWarning
    )
