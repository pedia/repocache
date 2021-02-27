import configparser
from repocache.server import Server

paths = [
    # pypi
    '/pypi/simple/click/',
    '/pypi/simple/click/click-7.1.2-py2.py3-none-any.whl',
    # mvn
    '/mvn/default/org/jdom/jdom/1.1/jdom-1.1.pom',
    '/mvn/default/xpp3/xpp3_min/1.1.4c/xpp3_min-1.1.4c.jar',
    # npm
    '/npm/default/color-name',
    '/npm/default/color-name/-/color-name-1.1.4.tgz',
    # yum
    '/centos/huawei/7/os/x86_64/Packages/libXtst-1.2.3-1.el7.x86_64.rpm',
    '/centos/sclo/Centos-7.repo',
    '/centos/sclo/Packages/r/rh-python36-2.0-1.el7.x86_64.rpm',
    # rust
    '/rust/index.html',
    '/rust/default/dist/channel-rust-stable.toml.sha256',
]


def test_paths():
  assert len(paths) == 11

  config = configparser.ConfigParser()
  config.read('default.cfg')
  assert len(config.sections()) > 0

  app = Server(config)
  client = app.test_client()
  for path in paths:
    rv = client.get(path)
    assert rv.status_code == 200, path
