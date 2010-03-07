### DESCRIPTION

This script + bashrc file provides a bash directory stack "cd history"
function. The bash function intercepts normal shell cd commands to
keep a stack of previous directories.

### USAGE

    cd somepath  : Add "somepath" to your directory stack and cd there.
    cd -l        : List the current stack and its indices.
    cd -n        : cd to stack index "n".
    cd -/string  : Search back through stack for "string" and cd there.
    cd --        : List the stack and its indices then prompt for dir to select.
    cd -h|?      : Print this help.

All other arguments are passed on to the normal cd command.

### INSTALLATION

Requires bash + python 2.x or later. Just type the following to install.

    sudo make install

and then each user who wants to use the cdhist facility should source
the bashrc_cdhist file into their bashrc, i.e from within ~/.bashrc just
add a line:

    source /usr/local/etc/bashrc_cdhist

Then log out and back in again.

In detail, make install merely installs the following files:

    /usr/local/etc/bashrc_cdhist
    /usr/local/bin/cdhist.py.

You can install these to your home area if you prefer.
Just ensure that CDHISTPROG_ in the bashrc_cdhist file points to
cdhist.py.

### LICENSE

Copyright (C) 2010 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <http://www.gnu.org/licenses/> for more details.
