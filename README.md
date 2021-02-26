# repocache
Universal caching and proxying repository server for pypi/maven/..., speedup local using.

## How to use repocache for mvn?

Change ~/.m2/settings.xml as:
```xml
<?xml version="1.0" encoding="UTF-8"?>
                <settings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                          xmlns="http://maven.apache.org/SETTINGS/1.0.0"
                          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
    <profiles>
        <profile>
            <id>repocache</id>
            <repositories>
                <repository>
                    <id>repocache</id>
                    <url>http://127.0.0.1:5000/mvn/default/</url>
                </repository>
                <repository>
                    <id>jitpack.io</id>
                    <url>http://127.0.0.1:5000/mvn/default/</url>
                </repository>
            </repositories>
        </profile>
    </profiles>
    <activeProfiles>
        <activeProfile>nexus</activeProfile>
    </activeProfiles>
    <mirrors>
        <mirror>
            <id>repocache</id>
            <url>http://127.0.0.1:5000/mvn/default/</url>
            <mirrorOf>central</mirrorOf>
        </mirror>
    </mirrors>
</settings>
```

```shell
pip install repocache

# Start repocache web server.
python -m repocache.main -f default.cfg

#
mvn install
```



## How to use repocache for pip?
```shell
pip install repocache

python -m repocache.main -f default.cfg

pip install -i http://127.0.0.1:5000/pypi/simple --trusted-host=127.0.0.1:5000 click==7.1.2
```

Or change ~/.pip/pip.conf as:
```
[global]
trusted-host=127.0.0.1:5000
index-url=http://127.0.0.1:5000/pypi/simple
```

## Settting file
See [default.cfg](default.cfg)


## Open source
This repository was copy from pypicache early, but fully rewrite later.
PR wellcome.
