# /public/com/fasterxml/jackson/jackson-parent/2.10/jackson-parent-2.10.pom

import json
import logging

import lxml.html
from flask import Blueprint, render_template, request

from pypicache.vendor import Vendor

mod = Blueprint(
    'mvn',
    __name__,
    url_prefix='/public',
    template_folder='templates/mvn',
    static_folder='static',
)


@mod.route('/<path:path>')
def handle(path):
  return f'path: {path}'


class Maven(Vendor):
  pass
