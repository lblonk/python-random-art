Developed as occasional past-time;
A python-based random art generation app.

### Summary ###

Consists of:

- Art-generation by nprandomart package,
 which is an expanded and optimized version of
 Andrej Bauer's Simple Random Art educational program.

- A web app (flask app)

### Demo ###

A demo is provided on http://blnkl.pythonanywhere.com

### Installation instructions; ###

- download python 3.7 or higher.

then, in the terminal;
- create a virtual-environment for this project (https://docs.python.org/3/library/venv.html)
- navigate into the 'artsgeneration' folder
- install the nprandomart package: `pip install -e .`  (`-e` installs as editable, 
so that you have the option to tweak and add to the functions later on)
- navigate into the 'webapp' folder
- install the webapp package: `pip install -e .`
- start the flask app (https://flask.palletsprojects.com/en/1.1.x/quickstart/)

### Example outputs: ###

![Alt text](webapp/rawebapp/static/example_images/purpleredorange.png?raw=true "example output")


![Alt text](webapp/rawebapp/static/example_images/brushes.png?raw=true "example output")


![Alt text](webapp/rawebapp/static/example_images/mandlegradient.bmp?raw=true "example output")