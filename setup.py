#!/usr/bin/env python
# -*- coding:utf-8 -*-

# NOTE(StaticCube) Guidelines for Major.Minor.Micro
# - Major means an API contract change
# - Minor means API bugfix or new functionality
# - Micro means change of any kind (unless significant enough for a minor/major).

import io
from setuptools import setup

setup(
  name = 'python-zyxelnas',
  packages = ['ZyxelNAS'], # this must be the same as the name above
  version = '0.0.1',
  description = 'Python API for communication with Zyxel NAS',
  author = 'FG van Zeelst (StaticCube), Oskar Joelsson (orrpan)',
  author_email = '',
  url = 'https://github.com/orrpan/python-zyxelnas',
  download_url = 'https://github.com/orrpan/python-zyxelnas',
  keywords = ['zyxelnas', 'zyxel'],
  classifiers = [],
  install_requires=[
    'requests>=1.0.0'
    'wakeonlan>=1.1.6'
    ]
)
