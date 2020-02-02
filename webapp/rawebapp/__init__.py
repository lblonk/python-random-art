import os,io
from flask import Flask, url_for, render_template, Response, Markup, json, jsonify
from .getimage import get_image, get_art
from werkzeug.wsgi import FileWrapper
import uuid
from nprandomart import tree_string

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

    app.expression_trees = LimitedSizeDict(size_limit=100)

    @app.route('/')
    def index():

        # make expression tree
        art = get_art()

        # store so it can be passed to other app functions by id
        art_id = uuid.uuid4().hex
        app.expression_trees[art_id] = art

        # create pretty text representation of expression tree
        tree_ascii = tree_string(art)
        # todo: plot tree with 2d plot of function at each node for each op,
        #  using http://etetoolkit.org/docs/latest/tutorial/tutorial_drawing.html#id30

        # return html page
        return render_template('image.html',
                               image_endpoint = url_for('image_file',art_id=art_id),
                               expression_tree = tree_ascii)

    @app.route('/image_file/<art_id>')
    def image_file(art_id):

        art = app.expression_trees[art_id]
        img = get_image(art)
        output = io.BytesIO()
        img.convert('RGBA').save(output, format='PNG')
        output.seek(0, 0)
        w = FileWrapper(output) #this is needed since Flask's send_file() does not work on pythonanywhere: https://www.pythonanywhere.com/forums/topic/13570/
        return Response(w, mimetype="image/png", direct_passthrough=True)

    return app


# special dict that keeps (only) the recent expression trees in memory
from collections import OrderedDict

class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self.size_limit = kwds.pop("size_limit", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)