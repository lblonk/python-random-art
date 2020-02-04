import os,io
from flask import Flask, url_for, render_template, Response, Markup, json, jsonify
from .getimage import get_image, get_art
from werkzeug.wsgi import FileWrapper
import uuid
from nprandomart import tree_as_ascii

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

    # a dict to hold the arts (expression trees) in memory so they can be used by multiple functions
    # (only the key 'art_id' is passed in the url to the endpoints)
    app.arts = LimitedSizeDict(size_limit=200)

    def get_art_id(min_arity = 20, max_arity = 150):
        """
        generate and store the art (expression tree), return its id
        :param min_arity: minimum complexity of the art
        :param max_arity: maximum complexity of the art
        """
        art_id = uuid.uuid4().hex

        # make expression tree
        art = get_art(min_arity , max_arity)

        # store so it can be passed to other app functions by id
        app.arts[art_id] = art
        return art_id

    def get_ascii(art_id):
        """ 
        return pretty text representation (ASCII-art) of expression tree

        """""
        art = app.arts[art_id]
        tree_ascii = tree_as_ascii(art)
        return tree_ascii

        # todo: plot tree with 2d plot of function result at each node for each operator,
        # using http://etetoolkit.org/docs/latest/tutorial/tutorial_drawing.html#id30

    def render_page(art_id,ascii):
        return render_template('image.html',
                               image_endpoint = url_for('image_file',art_id=art_id),
                               expression_tree = ascii)

    @app.route('/')
    def index():
        """ 1st call: the landing page."""
        art_id = get_art_id(min_arity=15,max_arity=30) # lower arity to start with to reduce initial loading time.
        ascii = get_ascii(art_id)
        return render_page(art_id,ascii)

    @app.route('/higher')
    def subsequent_calls():
        """ for subsequent calls (when the user clicks the button); return image of higher complexity"""
        art_id = get_art_id(min_arity=30,max_arity=80)
        ascii = get_ascii(art_id)
        return render_page(art_id, ascii)

    @app.route('/image_file/<art_id>')
    def image_file(art_id):
        """
        render and return the image itself
        """
        art = app.arts[art_id]
        img = get_image(art)
        output = io.BytesIO()
        img.convert('RGBA').save(output, format='PNG')
        output.seek(0, 0)
        w = FileWrapper(output) #this is needed since Flask's send_file() does not work on pythonanywhere: https://www.pythonanywhere.com/forums/topic/13570/
        return Response(w, mimetype="image/png", direct_passthrough=True)

    return app


# A utility: a special dict that keeps (only) the recent expression trees in memory
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