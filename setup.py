#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for the APRS Cursor-on-Target Gateway.

Source:: https://github.com/ampledata/aprscot
"""

import os
import sys

import setuptools

__title__ = 'aprscot'
__version__ = '3.0.0'
__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist')
        os.system('twine upload dist/*')
        sys.exit()


publish()


setuptools.setup(
    name=__title__,
    version=__version__,
    description='APRS Cursor-on-Target Gateway.',
    author='Greg Albrecht',
    author_email='oss@undef.net',
    packages=['aprscot'],
    package_data={'': ['LICENSE']},
    package_dir={'aprscot': 'aprscot'},
    license=open('LICENSE').read(),
    long_description=open('README.rst').read(),
    url='https://github.com/ampledata/aprscot',
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'aprslib',
        'pycot >= 1.0.0',
        'gexml'
    ],
    classifiers=[
        'Topic :: Communications :: Ham Radio',
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License'
    ],
    keywords=[
        'Ham Radio', 'APRS', 'Cursor on Target', 'ATAK', 'TAK', 'CoT'
    ],
    entry_points={'console_scripts': ['aprscot = aprscot.commands:cli']}
)
