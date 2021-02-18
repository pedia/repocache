import logging

from flask import (Flask, render_template, request)
from werkzeug.exceptions import NotFound

import pypicache.pypi
import pypicache.maven


class Server(Flask):
  def __init__(self):
    super(Server, self).__init__('repocache')

    vendors = {
        'pypi': pypicache.pypi,
        'mvn': pypicache.maven,
    }
    for _, p in vendors.items():
      self.register_blueprint(p.mod)


def configure_app(pypi,
                  package_store,
                  package_cache,
                  debug=False,
                  testing=False):
  app = Server()
  app.debug = debug
  app.testing = testing
  app.config["pypi"] = pypi
  app.config["package_store"] = package_store
  app.config["cache"] = package_cache

  return app


# @app.route("/")
def index():
  return render_template("index.html")
