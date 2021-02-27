from setuptools import setup

long_description = open('README.md').read()

setup(
    name='repocache',
    version='0.3.3',
    description='Universal caching and proxying server for pypi/maven/npm/yum',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pedia/repocache',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    author='repocache author',
    packages=['repocache'],
    package_data={
        'repocache': [
            'templates/yum/*.repo',
            'templates/pypi/*.html',
            'templates/*.html',
        ],
    },
    data_files=[('.', 'default.cfg')],
    install_requires=[
        'Flask',
        'filelock',
        'requests',
    ],
)
