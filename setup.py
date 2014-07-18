#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-citadel',
    version='0.1.3',
    description='Django Citadel - providing an encrypted ModelField',
    author='Christopher Bunn',
    author_email='',
    url='',
    packages=find_packages(),
    install_requires = [
        'pycrypto',
    ],
    test_suite="runtests.main"
)
