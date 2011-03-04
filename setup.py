#!/usr/bin/env python

from distutils.core import setup
import videokit

setup(
    name='videokit',
    version=videokit.__version__,
    description='A Django app to encode videos using videokit.',
    long_description=open('README.md').read(),
    author='Daniel J. Becker',
    url='http://github.com/danieljb/django-videokit',
    packages=('videokit',),
    requires=('celery', 'django-celery', 'videotool', 'django-hybrid-filefield'),
    license='GPL',
)
