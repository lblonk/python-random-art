"""
A simple script to use the flask app as a desktop app.
Requires PyQT5 to work
"""

from webui import WebUI #TODO consider benefits of pyfladesk (https://github.com/smoqadam/PyFladesk)
from rawebapp import create_app

app = create_app()
ui = WebUI(app, debug=True)

if __name__ == '__main__':
  ui.run()