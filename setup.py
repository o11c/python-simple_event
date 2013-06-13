#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='simple_event',
    version='1.0',
    description='A minimal, yet complete, event loop in pure python',
    author='Ben Longbons',
    author_email='b.r.longbons@gmail.com',
    url='http://github.com/o11c/python-simple_event',
    packages=[
        'simple_event'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
    ],
)
