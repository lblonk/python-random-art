import os,io
from flask import Flask, url_for, render_template, Response, Markup, json, jsonify,request
from werkzeug.wsgi import FileWrapper
import uuid
from .utitlities import LimitedSizeDict
from nprandomart import get_image, get_art
import jsonpickle
from json.decoder import JSONDecodeError

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

    def render_page(art_id):
        return render_template('image.html',
                               image_endpoint = url_for('image_file',art_id=art_id),
                               large_image_endpoint = url_for('large_image_file',art_id=art_id),
                               tree_image_endpoint = url_for('tree_image_file',art_id=art_id),
                               tree_file_endpoint =url_for('tree_file',art_id=art_id),
                               tree_file_upload_endpoint = url_for('tree_upload'))

    @app.route('/')
    def index():
        """ 1st call: the landing page."""
        art_id = get_art_id(min_arity=15,max_arity=30) # lower arity to start with to reduce initial loading time.
        return render_page(art_id)

    @app.route('/higher')
    def subsequent_calls():
        """ for subsequent calls (when the user clicks the button); return image of higher complexity"""
        art_id = get_art_id(min_arity=30,max_arity=80)
        return render_page(art_id)

    @app.route('/image_file/<art_id>')
    def image_file(art_id):
        """
        rendering for page view
        """
        return get_wrapped_image_file(art_id,size=900)

    @app.route('/large_image_file/<art_id>')
    def large_image_file(art_id):
        """
        rendering for printing
        """
        return get_wrapped_image_file(art_id,size=1920)

    def get_wrapped_image_file(art_id,size):
        """
        render and return the image itself
        """
        art = app.arts[art_id]
        img = get_image(art,size=size)
        output = io.BytesIO()
        img.convert('RGBA').save(output, format='PNG')
        output.seek(0, 0)
        w = FileWrapper(output) #this is needed since Flask's send_file() does not work on pythonanywhere: https://www.pythonanywhere.com/forums/topic/13570/
        return Response(w, mimetype="image/png", direct_passthrough=True)

    @app.route('/tree_file/<art_id>')
    def tree_file(art_id):
        """
        return the art as json
        :return:
        """
        jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
        art = app.arts[art_id]
        response = app.response_class(
            response=jsonpickle.encode(art),
            status=200,
            mimetype='application/json',
            headers={"Content-disposition":
                     f"attachment; filename={art_id}.json"} # as attachment; to trigger download
        )
        return response

    @app.route('/tree_upload', methods=['GET', 'POST'])
    def tree_upload():
        if request.method == 'POST':
            f = request.files['file']
            s = f.read()

            try:
                art = jsonpickle.decode(s)
            except JSONDecodeError as e:
                return f'Invalid JSON file: {e}'

            art_id = uuid.uuid4().hex
            app.arts[art_id] = art
            return render_page(art_id)


    @app.route('/tree_image_file/<art_id>')
    def tree_image_file(art_id):
        """
        render and return the image itself
        """
        art = app.arts[art_id]
        get_image(art, size = 200)
        from nprandomart.treevisualisation import get_tree_with_operator_images,plot_tree_with_images, as_bytesio
        tree = get_tree_with_operator_images(art)
        fig = plot_tree_with_images(tree)
        output = as_bytesio(fig)

        w = FileWrapper(output)
        return Response(w, mimetype="image/png", direct_passthrough=True)

    return app