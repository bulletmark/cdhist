#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

import stat
from pathlib import Path
from setuptools import setup

name = 'cdhist'
module = name.replace('-', '_')
here = Path(__file__).resolve().parent
executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH

setup(
    name=name,
    version='2.9',
    description='Program to provide a Linux cd history directory stack',
    long_description=here.joinpath('README.md').read_text(),
    long_description_content_type="text/markdown",
    url=f'https://github.com/bulletmark/{name}',
    author='Mark Blakeney',
    author_email='mark.blakeney@bullet-systems.net',
    keywords='bash zsh fzf',
    license='GPLv3',
    py_modules=[module],
    python_requires='>=3.4',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        (f'share/{name}', ['README.md', f'{name}.rc']),
    ],
    scripts=[f.name for f in here.iterdir() if f.name.startswith(name)
        and f.is_file() and f.stat().st_mode & executable],
)
