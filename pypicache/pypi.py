import json
import logging
import os

import lxml.html
import requests
from flask import render_template
from tornado.util import ObjectDict

from pypicache import exceptions
from pypicache.vendor import Vendor

# Forward compatible with python 3
try:
  import xmlrpc.client as xmlrpclib
  xmlrpclib  # shut pyflakes up
except ImportError:
  import xmlrpclib

logger = logging.getLogger(__name__)


def get_uri(uri):
  """Request the given URI and return the response

    Checks for 200 response and raises appropriate exceptions otherwise.

    """
  response = requests.get(uri)
  if response.status_code == 404:
    raise exceptions.NotFound("Can't locate {0}: {1}".format(uri, response))
  elif response.status_code != 200:
    raise exceptions.RemoteError('Unexpected response from {0}: {1}'.format(
        uri, response))
  return response


class PyPI(Vendor):
  def __init__(self, pypi_server='https://pypi.org/'):
    if not pypi_server.endswith('/'):
      pypi_server = pypi_server + '/'
    self.pypi_server = pypi_server
    # Certain operations aren't available via the JSON api (well, at least obviously)
    self.xmlrpc_client = xmlrpclib.ServerProxy('{0}pypi'.format(
        self.pypi_server))

  def get_versions(self, package, show_hidden=False):
    """Returns a list of available versions for a package

        This calls the PyPI XML-RPC API. See
        http://wiki.python.org/moin/PyPiXmlRpc

        :param package: Name of the package
        :param show_hidden: Show versions marked as hidden, can be very slow.
        :returns: A list of version strings
        """
    versions = self.xmlrpc_client.package_releases(package, show_hidden)
    logger.debug('Got versions {0} for package {1!r}'.format(versions, package))
    return versions

  def get_urls(self, package, version):
    """Get a list of URLS for the given package

        This takes the url info returned from the PyPI JSON API and only
        returns urls dicts.

        See http://wiki.python.org/moin/PyPiJson

        """
    uri = '{server}pypi/{package}/{version}/json'.format(
        server=self.pypi_server,
        package=package,
        version=version,
    )
    logger.info('Fetching JSON info from {0}'.format(uri))
    r = get_uri(uri)
    for url in json.loads(r.content)['urls']:
      yield url

  def get_simple_package_info(self, package, version=None):
    if version is None:
      version = ''
    if 'simple.' in self.pypi_server:
      simple = ''
    else:
      simple = 'simple/'
    uri = '{0}{1}{2}/{3}'.format(self.pypi_server, simple, package, version)
    r = get_uri(uri)
    return r.content
    # TODO WIP in progress, trying to reproduce a simple page with links only
    # Better still to rewrite using local urls
    # logger.info('Checking PyPI for links to {0}'.format(package))
    # links = []
    # for version in self.pypi_get_versions(package):
    #     logger.debug('Found package {0} version {1}'.format(package, version))
    #     for url in self.pypi_get_sdist_urls(package, version):
    #         logger.debug('Found link {0!r}'.format(url))
    #         links.append('<a href='{url}#md5={md5_digest}'>{filename}</a>'.format(**url))

    # logger.debug('Found links {0}'.format(links))
    # return SIMPLE_PACKAGE_PAGE_TEMPLATE.format(package=package, links='\n'.join(links))

  def get_file(self, package, filename, python_version=None):
    """

        :returns: package data

        """
    if python_version is not None:
      uri = '{0}packages/{1}/{2}/{3}/{4}'.format(self.pypi_server,
                                                 python_version, package[0],
                                                 package, filename)
    else:
      uri = '{0}packages/source/{1}/{2}/{3}'.format(self.pypi_server,
                                                    package[0], package,
                                                    filename)
    logger.debug('Fetching from {0}'.format(uri))
    r = get_uri(uri)
    return r.content

  def fetch_package_info(self, name, **kv):
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
    r = self.fetch(uri)

    root = lxml.html.fromstring(r.content)
    for i in root.xpath('//body/a'):
      print(i)
      raise Exception(i)

    return r.content

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

  def html2package(self, name, content):
    root = lxml.html.fromstring(content)

    return ObjectDict(
        name=name,
        files=[i for i in root.xpath('//body/a')],
    )

  def fetch_package(self, name, **kv):
    url = self.url4package(name, **kv)
    resp = self.fetch(url)
    return html2package(name, resp.content)

  def ensure_package(self, name, **kv):
    cache_filename = f'{name}.meta'

    url = self.url4package(name, **kv)
    return self.fetch_or_load_json(
        name,
        fetch_handle=lambda: self.fetch_package(name),
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
