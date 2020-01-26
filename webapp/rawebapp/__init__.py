import os,io
from flask import Flask, url_for, render_template, Response
from .getimage import get_image
from werkzeug.wsgi import FileWrapper

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
        # img = get_image()
        # dest_path = Path(app.root_path) /'static/newimage.bmp'
        #
        # if not dest_path.parent.exists():
        #     dest_path.parent.mkdir()
        # img.save(dest_path)
        return render_template('image.html')


    @app.route('/image_file')
    def image_file():
        img = get_image()
        output = io.BytesIO()
        img.convert('RGBA').save(output, format='PNG')
        output.seek(0, 0)
        # return send_file(output,mimetype='image/png', as_attachment=False,cache_timeout=0.0)
        w = FileWrapper(output) #this is needed since Flask's send_file() does not work on pythonanywhere: https://www.pythonanywhere.com/forums/topic/13570/
        return Response(w, mimetype="image/png", direct_passthrough=True)

    # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # crude solution to avoid browser caching generated images


    return app