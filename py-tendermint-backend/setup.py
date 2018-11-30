#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

DIR = path.abspath(path.dirname(__file__))

with open(path.join(DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytendermint',
    version='0.1.0',
    description='Python Tendermint client (HTTP)',
    long_description=long_description,
    url='https://github.com/davebryson/py-tendermint-client',
    author='Dave Bryson',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='tendermint',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        "requests>=2.13.0",
        "pytest>=3.0.7",
        "pytest-pythonpath>=0.7.1"
    ],
)
