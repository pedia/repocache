import requests
import os.path
import json
from tornado.util import ObjectDict


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
    TODO: timeout setting
    '''
    return requests.get(url)

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

    if os.path.exists(cache_name):
      # TODO: store a meta for expired
      return load_handle(open(cache_name, open_mode[0]).read())
    else:
      d = fetch_handle()

      if d is None:
        return

      if isinstance(d, requests.Response):
        d = d.content

      # ....
      if '/' in cache_name:
        folder = os.path.dirname(cache_name)
        if not os.path.exists(folder):
          os.makedirs(folder)

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
