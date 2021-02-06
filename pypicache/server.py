import logging
import mimetypes
import re

from flask import (Flask, abort, jsonify, make_response, render_template,
                   url_for, request)
from werkzeug.exceptions import NotFound

from pypicache import exceptions
from pypicache.pypi import PyPI

app = Flask("pypicache")


class Server:
  def __init__(self):
    self.vendors = {'pypi': PyPI}

  def register(self, name, vendor_class):
    self.vendors[name] = vendor_class


def configure_app(pypi,
                  package_store,
                  package_cache,
                  debug=False,
                  testing=False):
  app.debug = debug
  app.testing = testing
  app.config["pypi"] = pypi
  app.config["package_store"] = package_store
  app.config["cache"] = package_cache
  return app


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/simple/")
def simple_index():
  """The top level simple index page

    """
  return render_template(
      "simple.html",
      packages=app.config["package_store"].list_packages(),
  )


@app.route("/simple/<name>/")
def pypi_package(name):
  vendor = PyPI()
  p = vendor.ensure_package(name)
  if not p:
    raise NotFound

  return render_template('pypi/package_list.html', package=p)


@app.route("/simple/<name>/<filename>")
def pypi_package_file(name, filename):
  vendor = PyPI()
  p = vendor.ensure_package(name)
  if not p:
    raise NotFound

  return vendor.ensure_file(name, filename)

