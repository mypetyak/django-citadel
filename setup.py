#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-citadel',
    version='1.0.1',
    description='A Django app that provides an encrypted Model and ModelField',
    author='Christopher Bunn',
    url='https://github.com/mypetyak/django-citadel',
    packages=['citadel'],
    install_requires = [
        'pycrypto',
    ],
    test_suite="tests.runtests.run_all"
)
