#!/usr/bin/env python

import sys
import re
import os
from setuptools import setup, find_packages
import codecs

PACKAGES = find_packages(where='src')

KEYWORDS = ['UniProt', 'Database', 'Protein']

INSTALL_REQUIRES = [
    'sqlalchemy',
    'pandas',
    'pymysql',
    'requests',
    'click',
    'tqdm',
    'flasgger',
    'passlib',
    'wtforms',
    'configparser'
]

if sys.version_info < (3,):
    INSTALL_REQUIRES.append('configparser')

ENTRY_POINTS = {
    'console_scripts': [
        'pyuniprot = pyuniprot.cli:main',
    ]
}

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Build an absolute path from *parts* and return the contents of the resulting file. Assume UTF-8 encoding."""
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()

META_PATH = os.path.join('src', 'pyuniprot', '__init__.py')
META_FILE = read(META_PATH)


def find_meta(meta):
    """Extract __*meta*__ from META_FILE"""
    meta_match = re.search(
        r'^__{meta}__ = ["\']([^"\']*)["\']'.format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string'.format(meta=meta))


def get_long_description():
    """Get the long_description from the README.rst file. Assume UTF-8 encoding."""
    with codecs.open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

setup(
    name=find_meta('title'),
    version=find_meta('version'),
    url=find_meta('url'),
    author=find_meta('author'),
    author_email=find_meta('email'),
    maintainer='Christian Ebeling',
    maintainer_email=find_meta('email'),
    description=find_meta('description'),
    long_description=get_long_description(),
    keywords=KEYWORDS,
    license=find_meta('license'),
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database',
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    entry_points=ENTRY_POINTS,
)
