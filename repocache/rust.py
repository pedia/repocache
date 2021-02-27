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
  tail = name[len('rust.upstream.'):]
  return ObjectDict(name=tail, **section)


# RUSTUP_DIST_SERVER=https://static.rust-lang.org
# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh


class RustupRepository(ModularView, Vendor):
  @expose("/")
  def index(self):
    '''TODO: list cached packages'''
    return self.upstreams

  @expose("/index.html")
  def index_html(self):
    return render_template('rust/index.html')

  @expose("/rustup.sh")
  def sh(self):
    body = render_template('rust/rustup.sh')

    resp = make_response(body)
    resp.headers.set('Content-Type', 'text/plain')
    return resp

  @expose("/<string:un>")
  def root(self, un):
    ud = self.upstreams.get(un)
    if not ud:
      raise NotFound
    return ud

  @expose("/<string:un>/<path:filepath>")
  def file(self, un, filepath):
    # http://192.168.1.2:5000/rust/default/dist/channel-rust-stable.toml.sha256
    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    ud = ObjectDict(ud)
    url = ud.url
    del ud['url']

    f = self.fetch_or_load_binary(
        'rust/{}/{}'.format(un, filepath),
        fetch_handle=lambda: self.fetch('{}/{}'.format(url, filepath), **ud),
    )

    if filepath.endswith('.xz'):
      mimetype = 'application/x-tar'
    else:
      mimetype = 'application/octet-stream'
    return send_file(f, mimetype=mimetype)

  @expose("/<string:un>/-/v1/search")
  def search(self, un):
    ud = self.upstreams.get(un)
    if ud is None:
      raise NotFound

    resp = self.fetch(
        '{}/-/v1/search'.format(ud.url),
        params=request.args,
        **ud,
    )
    return resp.content

  # -/rust/v1/security/audits/quick
  @expose("/<string:un>/-/<path:left>", methods=('POST',))
  def other(self, un, left):
    print('post:', request)
    return ''

  def __init__(self, config):
    ModularView.__init__(
        self,
        name='rust',
        url_prefix='/rust',
    )

    self.upstreams = {}  # upstream name => Dict

    for section_name in config:
      if section_name.startswith('rust.upstream.'):
        u = create_upstream(section_name, config[section_name])
        self.upstreams[u.name] = u

  def _fetch(self, un, path):
    ud = self.upstreams.get(un)

    if ud is None:
      raise NotFound

    url = '{}/{}'.format(
        ud.url,
        path,
    )

    ud = ObjectDict(ud)
    del ud['url']

    return self.fetch(url, **ud)

  def ensure_package(self, un, name):
    # TODO: local
    jd = self.fetch_or_load_json(
        'rust/{}/{}.json'.format(un, name),
        fetch_handle=lambda: self._fetch(un, name),
    )

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
