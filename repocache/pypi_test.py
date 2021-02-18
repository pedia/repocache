import lxml.html
from repocache.pypi import PyPI

def test_pypi_html_parse():
  line1 = '''<a href="https://files.pythonhosted.org/packages/d2/3d/fa76db83bf75c4f8d338c2fd15c8d33fdd7ad23a9b5e57eb6c5de26b430e/click-7.1.2-py2.py3-none-any.whl#sha256=dacca89f4bfadd5de3d7489b7c8a566eee0d3676333fbb50030263894c38c0dc" data-requires-python="&gt;=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*">click-7.1.2-py2.py3-none-any.whl</a><br/>'''

  root = lxml.html.fromstring(line1)
  pf = PyPI.extract_line(root.xpath('a')[0])
  assert pf.filename == 'click-7.1.2-py2.py3-none-any.whl'
  assert pf.hash == 'sha256=dacca89f4bfadd5de3d7489b7c8a566eee0d3676333fbb50030263894c38c0dc'
  assert pf.type == 'wheel'
  assert pf.requires == '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*'
  assert '#' not in pf.url

  line2 = '''<a href="https://files.pythonhosted.org/packages/17/95/2028e02161ff874334008e853b1708d6b8d960218fd2f4bf9f6efd5de002/click-7.1.tar.gz#sha256=482f552f2d5452b9eeffc44165e8b790dd53f75bcce099a812b65e0357e860e2" data-requires-python="&gt;=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*">click-7.1.tar.gz</a><br/>'''

  root = lxml.html.fromstring(line2)
  pf = PyPI.extract_line(root.xpath('a')[0])
  assert pf.filename == 'click-7.1.tar.gz'
  assert pf.hash == 'sha256=482f552f2d5452b9eeffc44165e8b790dd53f75bcce099a812b65e0357e860e2'
  assert pf.type == 'source'
  assert pf.requires == '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*'
  assert '#' not in pf.url