# repocache
Universal caching and proxying server for pypi/maven, speedup local using.

## How to use repocache for mvn?
```shell
pip install repocache

python -m repocache.main --cache-folder=/tmp --mvn_upstream=http://maven.aliyun.com/nexus/content/groups/public
```

Change ~/.m2/settings.xml as:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://maven.apache.org/SETTINGS/1.0.0"
    xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
    <mirrors>
        <mirror>
            <id>repocache</id>
            <name>repo-local-mirror</name>
            <url>http://127.0.0.1:5000/mvn/public</url>
            <mirrorOf>central</mirrorOf>
        </mirror>
    </mirrors>
</settings>
```

## How to use repocache for pip?
```shell
pip install repocache

python -m repocache.main --cache-folder=/tmp
```

```shell
pip install -i http://127.0.0.1:5000/simple/ --trusted-host=127.0.0.1:5000 click==7.1.2
```

Or change ~/.pip/pip.conf as:
```
[global]
trusted-host=127.0.0.1:5000
index-url=http://127.0.0.1:5000/pypi/simple
```

## Settting file
See default.cfg


## dev now
```shell
# start http server
cd repocache
PYTHONPATH=.. python main.py --debug --reload /tmp/packages
```

This repository was copy from pypicache early, but fully rewrite later.
