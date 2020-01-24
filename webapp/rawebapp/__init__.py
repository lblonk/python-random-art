import os
from flask import Flask, url_for
from .getimage import get_image
from pathlib import Path

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        img = get_image()
        dest_path = Path(app.root_path) /'static/newimage.bmp'

        if not dest_path.parent.exists():
            dest_path.parent.mkdir()
        img.save(dest_path)
        return '<p>(refresh for new image)<p>' \
               '<img src=' + url_for('static', filename='newimage.bmp') + '>'

    return app