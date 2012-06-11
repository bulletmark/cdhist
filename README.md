## BASH CD HISTORY

This script + bashrc file provides a bash directory **cd history** stack.
The bash function calls a python helper script to intercept your shell
**cd** command and maintain a stack of directories visited which can be
listed and quickly jumped to by numeric index.

### USAGE

    cd somepath  : Add "somepath" to your directory stack and cd there.
    cd -l        : List the current stack and its indices.
    cd -n        : cd to stack index "n".
    cd -/string  : Search back through stack for REGEXP "string" and cd there.
    cd --        : List the stack and its indices then prompt for dir to select.
    cd -h|?      : Print this help.

All other arguments are passed on to the normal cd command.

### INSTALLATION

Requires bash + python 2.x or later (not python 3.x yet). Just type the
following to install.

    sudo make install

Each user who wants to use the cdhist facility should source the
bashrc_cdhist file into their bashrc, i.e from within ~/.bashrc just add
a line:

    source /usr/local/etc/bashrc_cdhist

Then log out and back in again.

In detail, make install merely installs the following system wide files:

    /usr/local/etc/bashrc_cdhist
    /usr/local/bin/cdhist.py

You can install these personally to your home area only if you prefer,
just type:

    make install

Which installs the following personal files:

    $HOME/.bashrc_cdhist
    $HOME/bin/cdhist.py

Then add the following to your ~/.bashrc:

    source ~/.bashrc_cdhist

### LICENSE

Copyright (C) 2010, 2012 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <http://www.gnu.org/licenses/> for more details.
