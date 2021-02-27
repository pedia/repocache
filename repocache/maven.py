import logging

from flask import Blueprint, make_response, render_template, request
from flask.helpers import send_file
from tornado.util import ObjectDict
from werkzeug.exceptions import NotFound

from repocache.modular_view import ModularView, expose
from repocache.vendor import Vendor

logger = logging.getLogger(__name__)


def create_upstream(name, section):
  '''create dict from section of ConfigParser'''
  tail = name[len('mvn.upstream.'):]
  return ObjectDict(name=tail, **section)


class Maven(ModularView, Vendor):
  @expose('/<string:un>/<path:fullname>')
  def handle(self, un, fullname):
    '''un: maven repository name'''
    f = self._ensure(un, fullname)
    if f is None:
      raise NotFound

    if fullname.endswith('.pom') or fullname.endswith('.xml'):
      mimetype = 'application/xml'
    elif fullname.endswith('.jar'):
      mimetype = 'application/java-archive'
    else:
      mimetype = 'application/octet-stream'

    return send_file(f, mimetype=mimetype)

  def __init__(self, config):
    ModularView.__init__(
        self,
        name='mvn',
        url_prefix='/mvn',
    )

    self.upstreams = {}  # upstream name => Dict

    for section_name in config:
      if section_name.startswith('mvn.upstream.'):
        u = create_upstream(section_name, config[section_name])
        self.upstreams[u.name] = u

  def _ensure(self, un, fullname):
    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    ud = ObjectDict(ud)
    prefix = ud['url']
    del ud['url']

    return self.fetch_or_load_binary(
        f'{un}/{fullname}',
        fetch_handle=lambda: self.fetch(f'{prefix}/{fullname}', **ud),
    )
