import lxml.html
from flask import Blueprint, make_response, render_template, request
from werkzeug.exceptions import NotFound

from repocache.vendor import Vendor

mod = Blueprint(
    'mvn',
    __name__,
    url_prefix='/public',
    template_folder='templates/mvn',
    static_folder='static',
)


@mod.route('/<path:fullname>')
def handle(fullname):
  content = Maven().any(fullname)
  if content is None:
    raise NotFound

  # TODO: Correct content-type
  return make_response(content)


class Maven(Vendor):
  def _fetch_any(self, fullname):
    # http://maven.fzzqxf.com/nexus/content/groups/public/io/netty/netty-codec-http/4.1.48.Final/netty-codec-http-4.1.48.Final.pom
    # https://maven.dremio.com/public/org/apache/calcite/calcite-core/1.16.0-202101020531550866-5383404/calcite-core-1.16.0-202101020531550866-5383404.jar
    # https://maven.dremio.com/public/org/apache/hadoop/hadoop-project-dist/3.2.1-dremio-202101121111520916-3f79071/hadoop-project-dist-3.2.1-dremio-202101121111520916-3f79071.pom
    # https://s3.amazonaws.com/redshift-maven-repository/release/io/grpc/grpc-netty/1.30.2/grpc-netty-1.30.2.jar
    # http://maven.aliyun.com/nexus/content/groups/public/io/grpc/grpc-netty/1.30.2/grpc-netty-1.30.2.jar

    upstream = [
        'http://maven.fzzqxf.com/nexus/content/groups/public',
        'http://maven.aliyun.com/nexus/content/groups/public',
    ]
    for u in upstream:
      url = '{}/{}'.format(
          u,
          fullname,
      )
      resp = self.fetch(url)
      if resp.status_code == 200:
        return resp

  def any(self, fullname):
    return self.fetch_or_load_binary(
        fullname,
        fetch_handle=lambda: self._fetch_any(fullname),
    )
