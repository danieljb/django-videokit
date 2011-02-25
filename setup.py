#!/usr/bin/env python

from distutils.core import setup

setup(
    name='videokit',
    version='0.2.0',
    description='A Django app to encode videos using videokit.',
    long_description=open('README.md').read(),
    author='Daniel J. Becker',
    url='http://github.com/danieljb/django-videokit',
    packages=('videokit',),
    license='GPL',
)