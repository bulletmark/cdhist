#!/usr/bin/python
# Setup script to install this package.
# M.Blakeney, Mar 2018.

import re, os
from setuptools import setup

here = os.path.dirname(os.path.abspath(__file__))
fullname = os.path.basename(here)
name = re.sub(r'-\d+\.\d+.*', '', fullname)
module = re.sub('-', '_', name)
readme = open(os.path.join(here, 'README.md')).read()

setup(
    name=name,
    version='1.5.4',
    description='Program to provide a bash cd history directory stack',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/bulletmark/{}'.format(name),
    author='Mark Blakeney',
    author_email='mark@irsaere.net',
    keywords='vim gvim',
    license='GPLv3',
    py_modules=[module],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        ('share/doc/{}'.format(name), ['README.md']),
        ('/etc', ['{}.bashrc'.format(name)]),
    ],
    scripts=[f for f in os.listdir(here)
        if os.path.isfile(f) and os.access(f, os.X_OK)]
)
