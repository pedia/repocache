import json
import logging
import os.path

import filelock
import requests
from tornado.util import ObjectDict
from werkzeug.exceptions import NotFound

logger = logging.getLogger(__name__)


def object_dict_create(o):
  '''init ObjectDict from normal dict'''
  assert isinstance(o, dict)
  d = ObjectDict(o)
  for k, v in d.items():
    if isinstance(v, dict):
      d[k] = object_dict_create(v)
    if isinstance(v, list):
      d[k] = [object_dict_create(i) for i in v]
  return d


class Vendor:
  def fetch(self, url, **kw):
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

    logger.debug('%s config %r to fetch args: %s retry: %s user-agent: %s', url,
                kw, args, retry, ua)

    while retry > 0:
      try:
        return requests.get(
            url,
            headers={
                'User-Agent': ua,
            },
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
      store_handle,
      load_handle,
      open_mode=None,
  ):
    if open_mode is None:
      open_mode = ('r', 'w')

    if os.path.isdir(cache_name):
      return

    if os.path.exists(cache_name) and os.stat(cache_name).st_size != 0:
      return load_handle(open(cache_name, open_mode[0]).read())
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
          if d.status_code != 200:
            raise NotFound

          d = d.content

        open(cache_name, open_mode[1]).write(store_handle(d))
        return d

  def fetch_or_load_json(self, cache_name, fetch_handle):
    return self.fetch_or_load(
        cache_name,
        fetch_handle,
        store_handle=lambda x: json.dumps(x),
        load_handle=lambda x: object_dict_create(json.loads(x)),
    )

  def fetch_or_load_binary(self, cache_name, fetch_handle):
    return self.fetch_or_load(
        cache_name,
        fetch_handle,
        store_handle=lambda x: x,
        load_handle=lambda x: x,
        open_mode=('rb', 'wb'),
    )
