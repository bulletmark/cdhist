#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

import re, stat
from pathlib import Path
from setuptools import setup

here = Path(__file__).resolve().parent
name = re.sub(r'-\d+\.\d+.*', '', here.name)
module = re.sub('-', '_', name)
readme = here.joinpath('README.md').read_text()
executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH

setup(
    name=name,
    version='1.4.2',
    description='Program to provide a bash cd history directory stack',
    long_description=readme,
    long_description_content_type="text/markdown",
    url=f'https://github.com/bulletmark/{name}',
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
        (f'share/doc/{name}', ['README.md']),
        (f'/etc', [f'{name}.bashrc']),
    ],
    scripts=[f.name for f in here.iterdir()
        if f.is_file() and f.stat().st_mode & executable]
)
