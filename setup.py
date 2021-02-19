from setuptools import setup

setup(
    name='repocache',
    version='0.1',
    description='Universal caching and proxying server for pypi/maven',
    url='https://github.com/pedia/repocache',
    packages=['repocache'],
    package_data={
        'repocache': ['templates'],
    },
    install_requires=[
        'certifi==0.0.8',
        'chardet==2.1.1',
        'distribute==0.6.34',
        'Flask==0.9',
        'Jinja2==2.6',
        'requests==1.1.0',
        'Werkzeug==0.8.3',
    ],
)
