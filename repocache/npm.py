import json
import logging

from flask import render_template, request, make_response, url_for
from flask.helpers import send_file
from tornado.util import ObjectDict
from werkzeug.exceptions import NotFound

from repocache.modular_view import ModularView, expose
from repocache.vendor import Vendor

logger = logging.getLogger(__name__)


def create_upstream(name, section):
  '''create dict from section of ConfigParser'''
  tail = name[len('npm.upstream.'):]
  return ObjectDict(name=tail, **section)


class NpmRepository(ModularView, Vendor):
  @expose("/")
  def index(self):
    '''TODO: list cached packages'''
    return self.upstreams

  @expose("/<string:un>/<string:name>")
  def package(self, un, name):
    '''/smallest-png'''
    jd = self.ensure_package(un, name)
    if not jd:
      raise NotFound

    return jd

  @expose("/<string:un>/<string:name>/-/<string:filename>")
  def package_file(self, un, name, filename):
    '''smallest-png/-/smallest-png-2.0.0-2.tgz'''
    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    jd = self.ensure_package(un, name)
    if not jd:
      raise NotFound

    for v, vd in jd.get('versions').items():
      if vd.dist.tarball.endswith(filename):
        ud = ObjectDict(ud)
        del ud['url']

        f = self.fetch_or_load_binary(
            'npm/{}/{}/{}'.format(un, name, filename),
            fetch_handle=lambda: self.fetch(vd.dist._url, **ud),
        )
        return send_file(f, mimetype='application/octet-stream')

    raise NotFound

  @expose("/<string:un>/-/v1/search")
  def search(self, un):
    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    resp = self.fetch('{}/-/v1/search'.format(ud.url),
                      params=request.args,
                      **ud)
    return resp.content

  # -/npm/v1/security/audits/quick
  @expose("/<string:un>/-/<path:left>", methods=('POST',))
  def other(self, un, left):
    print('post:', request)
    return ''

  def __init__(self, config):
    ModularView.__init__(
        self,
        name='npm',
        url_prefix='/npm',
    )

    self.upstreams = {}  # upstream name => Dict

    for section_name in config:
      if section_name.startswith('npm.upstream.'):
        u = create_upstream(section_name, config[section_name])
        self.upstreams[u.name] = u

  def _fetch(self, un, name):
    ud = self.upstreams.get(un)

    if ud is None:
      raise NotFound

    url = '{}/{}'.format(ud.url, name)

    ud = ObjectDict(ud)
    del ud['url']

    resp = self.fetch(url, **ud)
    if not resp.ok:
      raise NotFound

    return resp.json()

  def ensure_package(self, un, name):
    # TODO: local
    jd = self.fetch_or_load_json(
        'npm/{}/{}.json'.format(un, name),
        fetch_handle=lambda: self._fetch(un, name),
    )

    return self.fix(un, name, jd)

  def fix(self, un, name, jd):
    # replace `dist.tarball` as local url
    for v, vd in jd.get('versions').items():
      # if un in
      ud = self.upstreams.get(un)
      prefix = '{}/{}/-/'.format(ud.url, name)
      pos = vd.dist.tarball.find(prefix)
      if pos == 0:
        filename = vd.dist.tarball[pos + len(prefix):]
        vd.dist._url = vd.dist.tarball
        vd.dist.tarball = url_for(
            'npm.package_file',
            un=un,
            name=name,
            filename=filename,
            _external=True,
        )
    return jd
