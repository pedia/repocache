import json
import logging
import os.path

import filelock
import requests
from tornado.util import ObjectDict
from werkzeug.exceptions import NotFound

logger = logging.getLogger(__name__)


def create_object_dict(o):
  '''init ObjectDict from normal dict'''
  if isinstance(o, (str, int, float)):
    return o

  d = ObjectDict(o)
  for k, v in d.items():
    if isinstance(v, dict):
      d[k] = create_object_dict(v)
    if isinstance(v, list):
      d[k] = [create_object_dict(i) for i in v]
  return d


def write_to(fobj, fin):
  while True:
    buf = fin.read(8192)
    if buf:
      fobj.write(buf)
    else:
      break


class Vendor:
  cache_folder = None
  def fetch(self, url, params=None, **kw):
    '''http request
    keep trying for timeout error
    '''
    args = {
        'timeout': int(kw.get('timeout', 60)),
    }

    retry = int(kw.get('retry', 1))

    ua = kw.get(
        'user-agent',
        'Apache-Maven/3.6.0 (Java 1.8.0_202-release; Mac OS X 10.16)',
    )

    # proxy
    proxy_http = kw.get('http')
    if proxy_http:
      d = args.setdefault('proxies', {})
      d['http'] = proxy_http

    proxy_https = kw.get('https')
    if proxy_https:
      d = args.setdefault('proxies', {})
      d['https'] = proxy_https

    # auth
    if 'user' in kw and 'password' in kw:
      auth = requests.auth.HTTPBasicAuth(kw['user'], kw['password'])
      args['auth'] = auth

    logger.debug(' GET %s args: %r to: %s\n  retry: %s user-agent: %s', url, kw,
                 args, retry, ua)

    while retry > 0:
      try:
        return requests.get(
            url,
            headers={
                'User-Agent': ua,
            },
            params=params,
            **args,
        )
      except (requests.exceptions.Timeout, TimeoutError,
              requests.exceptions.ConnectionError):
        logger.warning('timeout for %s with args: %s', url, args)

      retry -= 1

  def fetch_or_load(
      self,
      cache_name,
      fetch_handle,
  ):
    '''
    fetch_handle type:
      def f(file: Stream) -> Stream:
    or
      def f(file: Stream) -> bytes:
    '''
    if os.path.isdir(cache_name):
      return

    # TODO: if cache_name.endswith('/)

    if Vendor.cache_folder is not None:
      cache_name = os.path.join(Vendor.cache_folder, cache_name)

    if os.path.exists(cache_name) and os.stat(cache_name).st_size != 0:
      return open(cache_name, 'rb')
    else:
      # create folder first
      if '/' in cache_name:
        folder = os.path.dirname(cache_name)
        if not os.path.exists(folder):
          os.makedirs(folder)

      # lock it
      lock = filelock.FileLock(cache_name)
      with lock.acquire():
        # download via http fetch
        d = fetch_handle()

        if d is None:
          return

        if isinstance(d, requests.Response):
          if not d.ok:
            raise NotFound

          with open(cache_name, 'wb') as f:
            for chunk in d:
              f.write(chunk)
          return open(cache_name, 'rb')
        elif isinstance(d, bytes):
          open(cache_name, 'wb').write(d)
        else:
          raise Exception('Unsupport type: {}'.format(type(d)))
        return d

  def fetch_or_load_binary(self, cache_name, fetch_handle):
    return self.fetch_or_load(cache_name, fetch_handle)

  def fetch_or_load_json(self, cache_name, fetch_handle):
    '''
    this `fetch_handle` return -> Dict
    return -> ObjectDict'''
    def dict2bytes(x):
      assert isinstance(x, dict)
      return json.dumps(x).encode('utf-8')

    f = self.fetch_or_load(
        cache_name,
        fetch_handle=lambda: dict2bytes(fetch_handle()),
    )

    if isinstance(f, bytes):
      return create_object_dict(json.loads(f.decode('utf-8')))

    # fix Python 3.5: the JSON object must be str, not 'bytes'
    # return create_object_dict(json.load(f))
    buf = f.read().decode('utf-8')
    return create_object_dict(json.loads(buf))
