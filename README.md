A cache server for speedup pypi/npm/mvn ...

# pypi/pip
```shell
# start http server
cd pypicache
PYTHONPATH=.. python main.py --debug /tmp/packages

# pip install with repocache
pip install -i http://127.0.0.1:5000/simple/ click
```
