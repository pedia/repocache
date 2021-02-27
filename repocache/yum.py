import logging

from flask import Blueprint, make_response, render_template, request, url_for
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


#
# YUM: Yellowdog Updater, Modified
#
class YumRepository(ModularView, Vendor):
  '''Most important URL
  http://192.168.1.2:5000/centos/sclo/repodata/repomd.xml
  http://mirrors.huaweicloud.com/centos/7.9.2009/sclo/x86_64/rh/repodata/repomd.xml
  '''
  @expose("/")
  def index(self):
    '''The top level simple index page'''
    # return render_template("pypi-index.html", packages=[])
    return self.upstreams

  @expose('/<string:un>/Centos-<int:version>.repo')
  def desc(self, un, version):
    ud = self.upstreams.get(un)
    if not ud:
      raise NotFound

    try:
      # try special .repo template first
      body = render_template(
          f'yum/{un}.repo',
          domain=url_for('centos.handle', un=un, fullname='', _external=True),
          version=version,
      )
    except:
      # univasal .repo
      body = render_template(
          'yum/centos.repo',
          domain=url_for('centos.handle', un=un, fullname='', _external=True),
          version=version,
      )

    resp = make_response(body)
    resp.headers.set('Content-Type', 'text/plain')
    return resp

  @expose('/<string:un>/<path:fullname>')
  def handle(self, un, fullname):
    '''un: repository name'''

    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    ud = ObjectDict(ud)
    url = ud.url
    del ud['url']

    f = self.fetch_or_load_binary(
        f'{un}/{fullname}',
        fetch_handle=lambda: self.fetch(f'{url}/{fullname}', **ud),
    )
    if fullname.endswith('.repo') or fullname.endswith(
        'readme') or fullname.endswith('.txt'):
      mimetype = 'text/plain'
    elif fullname.endswith('.rpm'):
      mimetype = 'application/x-redhat-package-manager'
    elif fullname.endswith('.xml'):
      mimetype = 'text/xml'
    else:
      mimetype = 'application/octet-stream'

    return send_file(f, mimetype=mimetype)

  def __init__(self, config):
    ModularView.__init__(
        self,
        name='centos',
        url_prefix='/centos',
    )

    self.upstreams = {}  # upstream name => Dict

    for section_name in config:
      if section_name.startswith('yum.upstream.'):
        u = create_upstream(section_name, config[section_name])
        self.upstreams[u.name] = u
