import logging

import lxml.html
from flask import Blueprint, make_response, render_template, request
from werkzeug.exceptions import NotFound

from vendor import Vendor

logger = logging.getLogger(__name__)

mod = Blueprint(
    'mvn',
    __name__,
    url_prefix='/mvn',
    template_folder='templates/mvn',
    static_folder='static',
)


@mod.route('/<string:rid>/<path:fullname>')
def handle(rid, fullname):
  '''rid: maven repository id'''
  content = Maven().any(fullname)
  if content is None:
    raise NotFound

  # print(request.headers)
  '''fuck mvn GET with:
  Cache-Control: no-cache
  Cache-Store: no-store
  Pragma: no-cache'''

  resp = make_response(content)
  resp.cache_control.max_age = 86400

  if fullname.endswith('.pom') or fullname.endswith('.xml'):
    resp.headers['content-type'] = 'application/xml'
    return resp

  return resp


@mod.route('/<path:fullname>')
def handle_default(fullname):
  content = Maven().any(fullname)
  if content is None:
    raise NotFound

  resp = make_response(content)
  resp.cache_control.max_age = 86400

  if fullname.endswith('.pom') or fullname.endswith('.xml'):
    resp.headers['content-type'] = 'application/xml'
    return resp

  return resp


class Maven(Vendor):
  def _upstream_for(self, fullname):
    # TODO: more upstream
    # dremio.com / free
    if 'redshift' in fullname:
      return (
          'https://s3.amazonaws.com/redshift-maven-repository/release',
          'http://maven.aliyun.com/nexus/content/groups/public',
      )
    elif 'dremio' in fullname or 'arrow' in fullname:
      return (
          'https://maven.dremio.com/public',
          'https://maven.dremio.com/free',
          'http://maven.aliyun.com/nexus/content/groups/public',
      )
    else:
      return (
          'http://maven.aliyun.com/nexus/content/groups/public',
          'https://maven.dremio.com/public',
      )

  def _fetch_any(self, fullname):
    for upstream in self._upstream_for(fullname):
      url = '{}/{}'.format(
          upstream,
          fullname,
      )
      resp = self.fetch(url)
      if resp.status_code == 200:
        logger.info('fetch %s/%s', upstream, fullname)
        return resp

    logger.info('failed %s', fullname)

  def any(self, fullname):
    return self.fetch_or_load_binary(
        fullname,
        fetch_handle=lambda: self._fetch_any(fullname),
    )
