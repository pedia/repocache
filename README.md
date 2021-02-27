# repocache
Universal caching and proxying repository server for pypi/maven/npm/yum, speedup local using.

## How to startup?
```bash
pip install repocache

python -m repocache.main -f default.cfg
# listen at 0.0.0.0:5000
```

## How to use repocache as YUM repository?
```bash
cd /etc/yum.repos.d

# base
curl -O http://192.168.1.2:5000/centos/huawei/Centos-7.repo
# sclo
curl -O http://192.168.1.2:5000/centos/sclo/Centos-7.repo

yum makecache
```

## How to use repocache as NPM repository?
```bash
npm config set registry https://127.0.0.1:5000/npm/default/
npm config set prefix=$HOME/.node_modules_global
npm --verbose install smallest-png@2.0.0 -g
```

## How to use repocache as MVN repository?

Change $HOME/.m2/settings.xml as:
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
                    <url>http://127.0.0.1:5000/mvn/jitpack/</url>
                </repository>
            </repositories>
        </profile>
    </profiles>
    <activeProfiles>
        <activeProfile>repocache</activeProfile>
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
cd /path/to/java-project
mvn install
```



## How to use repocache as PIP repository?
Simply install in shell:
```bash
pip install -i http://127.0.0.1:5000/pypi/simple --trusted-host=127.0.0.1:5000 click==7.1.2
```

Or change $HOME/.pip/pip.conf as:
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
