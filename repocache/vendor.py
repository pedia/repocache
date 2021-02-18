import json
import logging
import os.path

import filelock
import requests
from tornado.util import ObjectDict

logger = logging.getLogger(__name__)


def object_dict_create(o):
  '''create ObjectDict from dict'''
  assert isinstance(o, dict)
  d = ObjectDict(o)
  for k, v in d.items():
    if isinstance(v, dict):
      d[k] = object_dict_create(v)
    if isinstance(v, list):
      d[k] = [object_dict_create(i) for i in v]
  return d


class Vendor:
  def fetch(self, url):
    '''http request
    keep trying for timeout error
    '''
    timeout = 60
    while timeout < 1000:
      try:
        return requests.get(
            url,
            timeout=timeout,
            headers={
                'User-Agent':
                    'Apache-Maven/3.6.0 (Java 1.8.0_202-release; Mac OS X 10.16)',
            },
        )
      except (requests.exceptions.Timeout, TimeoutError,
              requests.exceptions.ConnectionError):
        logger.info('timeout(%d) for %s', timeout, url)
        timeout += 120

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
        # download via fetch
        d = fetch_handle()

        if d is None:
          return

        if isinstance(d, requests.Response):
          d = d.content

        open(cache_name, open_mode[1]).write(store_handle(d))
        return d

  def fetch_or_load_json(self, cache_name, fetch_handle):
    return self.fetch_or_load(
        cache_name,
        fetch_handle,
        store_handle=lambda content: json.dumps(content),
        load_handle=lambda file_content: object_dict_create(
            json.loads(file_content)),
    )

  def fetch_or_load_binary(self, cache_name, fetch_handle):
    return self.fetch_or_load(
        cache_name,
        fetch_handle,
        store_handle=lambda content: content,
        load_handle=lambda file_content: file_content,
        open_mode=('rb', 'wb'),
    )
