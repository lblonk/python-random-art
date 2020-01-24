import pytest
from rawebapp import create_app

@pytest.fixture
def app():
    app = create_app({'TESTING':True})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_new_image(client):
    response = client.get('/')
    assert response.data == b'<img src=/static/newimage.bmp>'
