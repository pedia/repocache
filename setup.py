from setuptools import setup

setup(
    name='repocache',
    version='0.2',
    description='Universal caching and proxying server for pypi/maven',
    url='https://github.com/pedia/repocache',
    author='repocache author',
    packages=['repocache'],
    package_data={
        'repocache': [
            'templates/pypi/*.html',
            'templates/*.html',
        ],
    },
    install_requires=[
        'Flask',
        'filelock',
        'requests',
    ],
)
