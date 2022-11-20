#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

from pathlib import Path
from setuptools import setup

name = 'cdhist'
module = name.replace('-', '_')
here = Path(__file__).resolve().parent

setup(
    name=name,
    version='3.4',
    description='Program to provide a Linux cd history directory stack',
    long_description=here.joinpath('README.md').read_text(),
    long_description_content_type="text/markdown",
    url=f'https://github.com/bulletmark/{name}',
    author='Mark Blakeney',
    author_email='mark.blakeney@bullet-systems.net',
    keywords='bash zsh cd fzf git worktree',
    license='GPLv3',
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    packages=[module],
    entry_points={
        'console_scripts': [f'{name}={module}.{module}:main'],
    },
)
