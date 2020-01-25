import pytest
from rawebapp import create_app
from flask_testing import TestCase

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
    assert 'src=/static/newimage.bmp>' in str(response.data) #TODO more thorough test