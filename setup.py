#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

test_requires = [
    'pytest >= 2.3.0',
    'pytest-xdist >= 1.8',
    'psutil >= 1.0.1'
]

setup(name='Layers',
    version='1.0',
    description='Layer templating system using wand.py',
    author='Ashley Minshall',
    author_email='aminshall2909@gmail.com',
    # requires=['wand >= 0.5.5'],
    tests_require=test_requires,
    # url='https://www.python.org/sigs/distutils-sig/',
    # packages=['distutils', 'distutils.command'],
)
