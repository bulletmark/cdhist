## BASH CD HISTORY

This script + bashrc file provides a bash directory **cd history** stack.
The bash function calls a python helper script to intercept your shell
**cd** command and maintain a stack of directories visited which can be
listed and quickly jumped to by numeric index.

### USAGE

    cd somepath  : Add "somepath" to your directory stack and cd there.
    cd -l        : List the current stack and its indices.
    cd -n        : cd to stack index "n".
    cd -/string  : Search back through stack for "string" and cd there.
    cd --        : List the stack and its indices then prompt for dir to select.
    cd -h|?      : Print this help.

All other arguments are passed on to the normal cd command.

### INSTALLATION

NOTE: Arch users can just install
[_cdhist from the AUR_](https://aur.archlinux.org/packages/cdhist/) and
skip to the next section.

Requires bash + python 2.6 or later (and is compatible with python 3+).
Just type the following to install.

    git clone http://github.com/bulletmark/cdhist
    cd cdhist
    sudo make install

In detail, make install merely installs the following system wide files:

    /usr/bin/cdhist
    /etc/cdhist.bashrc

### CONFIGURATION

Each user who wants to use the cdhist facility should source the
`/etc/cdhist.bashrc` file into their bashrc, i.e in `~/.bashrc`
just add:

    if [ -f /etc/cdhist.bashrc]; then
	source /etc/cdhist.bashrc
    fi

Then log out and back in again.

NOTE: _cdhist_ now installs system-wide but old versions installed
as local user files so to ensure that any old user configuration is
removed type the following as your normal user (i.e. not sudo/root).

    cdhist-setup clean

You can type this any time so no harm is done running it to make sure.

### UPGRADE

    cd cdhist  # Source dir, as above
    git pull
    sudo make install

### REMOVAL

    sudo cdhist-setup uninstall

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
