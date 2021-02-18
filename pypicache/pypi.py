import json
import logging

import lxml.html
from flask import Blueprint, render_template, request
from tornado.util import ObjectDict

from pypicache.vendor import Vendor

logger = logging.getLogger(__name__)

mod = Blueprint(
    'pypi',
    __name__,
    url_prefix='/simple',
    template_folder='templates/pypi',
    static_folder='static',
)


@mod.route("/")
def simple_index():
  """The top level simple index page

    """
  return render_template(
      "simple.html",
      packages=app.config["package_store"].list_packages(),
  )


@mod.route("/<name>/")
def pypi_package(name):
  vendor = PyPI()
  p = vendor.ensure_package(name)
  if not p:
    raise NotFound

  return render_template('pypi/file_list.html', package=p)


@mod.route("/<name>/<filename>")
def pypi_package_file(name, filename):
  vendor = PyPI()
  p = vendor.ensure_package(name)
  if not p:
    raise NotFound

  return vendor.ensure_file(name, filename)


class PyPI(Vendor):
  def __init__(self, pypi_server='https://pypi.org/'):
    if not pypi_server.endswith('/'):
      pypi_server = pypi_server + '/'
    self.pypi_server = pypi_server

  ##
  @staticmethod
  def extract_line(tag):
    '''parse html into a package file
    '''
    url = tag.attrib.get('href')
    if tag.text.endswith('.whl'):
      type = 'wheel'
    else:
      type = 'source'
    pf = ObjectDict(
        filename=tag.text,
        type=type,
        url=url.split('#')[0],
        hash=url.split('#')[1],
    )
    requires = tag.attrib.get('data-requires-python')
    if requires:
      pf.requires = requires
    return pf

  def _html2package(self, name, content):
    root = lxml.html.fromstring(content)

    return ObjectDict(
        name=name,
        files=[self.extract_line(i) for i in root.xpath('//body/a')],
    )

  def _fetch_package(self, name, **kv):
    url = self.url4package(name, **kv)
    resp = self.fetch(url)
    return self._html2package(name, resp.content)

  def ensure_package(self, name, **kv):
    cache_filename = f'{name}.meta'

    url = self.url4package(name, **kv)
    return self.fetch_or_load_json(
        name,
        fetch_handle=lambda: self._fetch_package(name),
    )

  def url4package(self, name, **kv):
    if 'simple.' in self.pypi_server:
      simple = ''
    else:
      simple = 'simple/'
    uri = '{}{}{}/{version}'.format(
        self.pypi_server,
        simple,
        name,
        version=kv.get('version', ''),
    )
    return uri

  def ensure_file(self, name, filename):
    p = self.ensure_package(name)
    for pf in p.files:
      if pf.filename == filename:
        return self.fetch_or_load_binary(
            pf.filename,
            lambda: self.fetch(pf.url).content,
        )
