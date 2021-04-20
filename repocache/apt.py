import logging

from flask import Blueprint, make_response, render_template, request, url_for
from flask.helpers import send_file
from tornado.util import ObjectDict
from werkzeug.exceptions import NotFound

from repocache.modular_view import ModularView, expose
from repocache.vendor import Vendor

logger = logging.getLogger(__name__)


#
# APT: Advanced Packaging Tools
# https://wiki.debian.org/SecureApt
class AptRepository(ModularView, Vendor):
  @expose("/index.json")
  def index(self):
    '''The top level simple index page'''
    # return render_template("pypi-index.html", packages=[])
    return self.upstreams

  @expose('/<string:un>/<string:version>/sources.list')
  def desc(self, un, stub='', version=7):
    ud = self.upstreams.get(un)
    if not ud:
      raise NotFound

    try:
      # try special .repo template first
      body = render_template(
          'apt/{}.repo'.format(un),
          domain=url_for('apt.handle', un=un, fullname='', _external=True),
          version=version,
      )
    except:
      # univasal .repo
      body = render_template(
          'apt/sources.list',
          domain=url_for('apt.handle', un=un, fullname='', _external=True),
          version=version,
      )

    resp = make_response(body)
    resp.headers.set('Content-Type', 'text/plain')
    return resp

  # TODO: maybe implement 3 function is better
  # @expose('/<string:un>/debian/<path:fullname>')
  # @expose('/<string:un>/dists/<path:fullname>')
  # @expose('/<string:un>/debian-security/<path:fullname>')
  @expose('/<string:un>/<path:fullname>')
  def handle(self, un, fullname):
    '''un: repository name
    curl -vs http://192.168.1.3:5000/debian/huawei/debian/dists/buster/InRelease
    curl -vs http://192.168.1.3:5000/debian/huawei/debian-security/dists/buster/updates/InRelease
    curl -vs http://192.168.1.3:5000/debian/huawei/debian/dists/buster-updates/InRelease

        https://repo.huaweicloud.com/debian/dists/buster/InRelease
        https://repo.huaweicloud.com/debian/dists/buster-updates/InRelease
        https://repo.huaweicloud.com/debian-security/dists/buster/updates/InRelease
        https://repo.huaweicloud.com/debian-cd
    '''

    print('>> handle', un, fullname)

    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    return self._fetch(un, fullname)

  def _fetch(self, un, fullname):
    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    ud = ObjectDict(ud)
    url = ud.url
    del ud['url']

    f = self.fetch_or_load_binary(
        '{}/{}'.format(un, fullname),
        fetch_handle=lambda: self.fetch('{}/{}'.format(url, fullname), **ud),
    )
    if fullname.endswith('.repo') or fullname.endswith(
        'readme') or fullname.endswith('.txt'):
      mimetype = 'text/plain'
    elif fullname.endswith('.deb'):
      mimetype = 'application/x-debian-package'
    elif fullname.endswith('.xml'):
      mimetype = 'text/xml'
    else:
      mimetype = 'application/octet-stream'

    return send_file(f, mimetype=mimetype)

  def __init__(self, config):
    ModularView.__init__(
        self,
        name='debian',
        url_prefix='/debian',
    )

    def create_upstream(name, section):
      '''create dict from section of ConfigParser'''
      print(name, section)
      tail = name[len('debian.upstream.'):]
      return ObjectDict(name=tail, **section)

    self.upstreams = {}  # upstream name => Dict

    for section_name in config:
      if section_name.startswith('debian.upstream.'):
        u = create_upstream(section_name, config[section_name])
        self.upstreams[u.name] = u
