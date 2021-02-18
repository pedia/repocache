# repocache
Universal caching and proxying server for pypi/mavn, speedup local using.

## How to use for mvn?
```shell
pip install repocache

python repocache.main --cache-folder=/tmp --mvn_upstream=http://maven.aliyun.com/nexus/content/groups/public
```

Change ~/.m2/settings.xml as:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://maven.apache.org/SETTINGS/1.0.0"
    xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
    <mirrors>
        <mirror>
            <id>maven.net.cn</id>
            <name>one of the central mirrors in china</name>
            <url>http://127.0.0.1:5000/public/</url>
            <mirrorOf>central</mirrorOf>
        </mirror>
    </mirrors>
</settings>
```

## How to use for pip?
```shell
pip install repocache

python repocache.main --cache-folder=/tmp
```

```shell
pip install -i http://127.0.0.1:5000/simple/ --trusted-host=127.0.0.1:5000 click
```

Or change ~/.pip/pip.conf as:
```
[global]
trusted-host=127.0.0.1:5000
index-url=http://127.0.0.1:5000/pypi/simple
```


## dev now
```shell
# start http server
cd pypicache
PYTHONPATH=.. python main.py --debug --reload /tmp/packages
```
