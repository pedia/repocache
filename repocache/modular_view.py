from flask import Blueprint


def expose(url='/', methods=('GET',)):
  """
    Use this decorator to expose views in your view classes.

    :param url:
        Relative URL for the view
    :param methods:
        Allowed HTTP methods. By default only GET is allowed.
    """
  def wrap(f):
    if not hasattr(f, '_urls'):
      f._urls = []
    f._urls.append((url, methods))
    return f

  return wrap


class _PatchedType(type):
  def __init__(cls, classname, bases, fields):
    type.__init__(cls, classname, bases, fields)

    # Gather exposed views
    cls._urls = []
    cls._default_view = None

    for p in dir(cls):
      attr = getattr(cls, p)

      if hasattr(attr, '_urls'):
        # Collect methods
        for url, methods in attr._urls:
          cls._urls.append((url, p, methods))

          if url == '/':
            cls._default_view = p


class ModularView(metaclass=_PatchedType):
  def __init__(
      self,
      name=None,
      url_prefix=None,
      template_folder=None,
      static_folder=None,
  ):
    if name is None:
      name = self.__class__.__name__
    self.name = name

    if url_prefix is None:
      url_prefix = '/'
    self.url_prefix = url_prefix

    if template_folder is None:
      template_folder = 'template'
    self.template_folder = template_folder

    if static_folder is None:
      static_folder = 'static'
    self.static_folder = static_folder

  def create_blueprint(self):
    '''Create Flask blueprint.'''
    # Create blueprint and register rules
    self.blueprint = Blueprint(
        self.name,
        self.__class__.__name__,
        url_prefix=self.url_prefix,
        template_folder=self.template_folder,
        static_folder=self.static_folder,
    )

    for url, name, methods in self._urls:
      self.blueprint.add_url_rule(
          url,
          name,
          getattr(self, name),
          methods=methods,
      )

    return self.blueprint

  def template_folder(self):
    return 'templates'

  def static_folder(self):
    return 'static'


class FooView(ModularView):
  @expose('/')
  def index(self):
    return 'module foo index'

  @expose('/a')
  def a(self):
    return 'module foo.a'
