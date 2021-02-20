import logging

from flask import Blueprint, Flask, render_template, request
from werkzeug.exceptions import NotFound

import maven
import pypi
import modular_view

mod = Blueprint(
    'server',
    __name__,
    url_prefix='/',
    template_folder='templates',
    static_folder='static',
)


class Server(Flask):
  def __init__(self, config):
    super(Server, self).__init__(__name__)
    self.vendor_config = config

    vendors = {
        'pypi': pypi.PyPI(config),
        'mvn': maven.Maven(config),
    }
    for _, p in vendors.items():
      self.register_blueprint(p.create_blueprint())

    self.register_blueprint(mod)
    # self.register_blueprint(modular_view.FooView().create_blueprint())
    # self.register_blueprint(pypi.PyPI().create_blueprint())

    # TODO: blueprint for local package upload

  def dump_urls(self):
    # copy from flask_script.commands.ShowUrls
    rows = []
    column_length = 0
    column_headers = ('Rule', 'Endpoint', 'Arguments')

    rules = sorted(self.url_map.iter_rules(),
                   key=lambda rule: getattr(rule, 'rule'))
    for rule in rules:
      rows.append((rule.rule, rule.endpoint, None))
    column_length = 2

    str_template = ''
    table_width = 0

    if column_length >= 1:
      max_rule_length = max(len(r[0]) for r in rows)
      max_rule_length = max_rule_length if max_rule_length > 4 else 4
      str_template += '%-' + str(max_rule_length) + 's'
      table_width += max_rule_length

    if column_length >= 2:
      max_endpoint_length = max(len(str(r[1])) for r in rows)
      # max_endpoint_length = max(rows, key=len)
      max_endpoint_length = max_endpoint_length if max_endpoint_length > 8 else 8
      str_template += '  %-' + str(max_endpoint_length) + 's'
      table_width += 2 + max_endpoint_length

    if column_length >= 3:
      max_arguments_length = max(len(str(r[2])) for r in rows)
      max_arguments_length = max_arguments_length if max_arguments_length > 9 else 9
      str_template += '  %-' + str(max_arguments_length) + 's'
      table_width += 2 + max_arguments_length

    print(str_template % (column_headers[:column_length]))
    print('-' * table_width)

    for row in rows:
      print(str_template % row[:column_length])


@mod.route("/")
def index():
  return render_template("index.html")
