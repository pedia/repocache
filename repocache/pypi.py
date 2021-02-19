import json
import logging

import lxml.html
from flask import render_template, request
from tornado.util import ObjectDict
from werkzeug.exceptions import NotFound

from modular_view import ModularView, expose
from vendor import Vendor

logger = logging.getLogger(__name__)


def create_upstream(name, section):
  '''create isnance from section of ConfigParser'''
  tail = name[len('pypi.upstream.'):]
  return ObjectDict(name=tail, **section)


class PyPI(ModularView, Vendor):
  @expose("/")
  def simple_index(self):
    '''The top level simple index page'''
    # return render_template("pypi-index.html", packages=[])
    return self.upstreams

  @expose("/<string:upstream>/<string:name>/")
  def pypi_package(self, upstream, name):
    p = self.ensure_package(upstream, name)
    if not p:
      raise NotFound

    return render_template('pypi/file_list.html', package=p)

  @expose("/<string:upstream>/<string:name>/<string:filename>")
  def pypi_package_file(self, upstream, name, filename):

    p = self.ensure_package(upstream, name)
    if not p:
      raise NotFound

    return self.ensure_file(upstream, name, filename)

  def __init__(self, config):
    ModularView.__init__(
        self,
        name='pypi',
        url_prefix='/pypi',
        template_folder='template/pypi',
        static_folder='static',
    )

    self.upstreams = {}  # name => Dict

    for section_name in config:
      if section_name.startswith('pypi.upstream.'):
        u = create_upstream(section_name, config[section_name])
        self.upstreams[u.name] = u

  @staticmethod
  def extract_line(tag):
    '''parse html line into a package file
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

  def _fetch_package(self, upstream, name, **kv):
    url = self._url4package(upstream, name, **kv)
    resp = self.fetch(url)
    return self._html2package(name, resp.content)

  def ensure_package(self, upstream, name, **kv):
    # TODO: local
    return self.fetch_or_load_json(
        f'{upstream}/{name}.json',
        fetch_handle=lambda: self._fetch_package(name),
    )

  def _url4package(self, upstream, name, **kv):
    ud = self.upstreams.get(upstream)

    if ud is None:
      raise NotFound

    uri = '{}/{}/{version}'.format(
        ud.url,
        name,
        version=kv.get('version', ''),
    )
    return uri

  def ensure_file(self, upstream, name, filename):
    p = self.ensure_package(upstream, name)
    for pf in p.files:
      if pf.filename == filename:
        # TODO: local
        return self.fetch_or_load_binary(
            pf.filename,
            lambda: self.fetch(pf.url).content,
        )
