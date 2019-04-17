## BASH SHELL CD HISTORY

[cdhist](http://github.com/bulletmark/cdhist) is a utility which
provides a bash shell **cd history** directory stack. A bash `cd` alias
calls a python helper script to intercept your normal shell `cd` command
and maintain a stack of directories you previously visited which can be
listed and quickly jumped to by numeric index.

The latest version and documentation is available at
http://github.com/bulletmark/cdhist.

### USAGE

Add "somepath" to your directory stack and cd there:

```
cd somepath
```

List the current stack and its indices:

```
cd -l
```

Change dir to stack index "n":

```
cd -n
```

Search back through stack for "string" and cd there:

```
cd -/string
```

List the stack and its indices then immediately prompt for dir to
select:

```
cd --
```

You can also type `/string` at the above prompt to search.

Show this help:

```
cd -h|?
```

All other arguments are passed on to the normal cd command.

### INSTALLATION

Arch users can install [cdhist from the
AUR](https://aur.archlinux.org/packages/cdhist/) and skip to the next
section.

Requires `python-setuptools` installed.

Requires bash + python 2.6 or later (and is compatible with python 3+).
Note [cdhist is on PyPI](https://pypi.org/project/cdhist/) so you can
`sudo pip install cdhist` or:

```
git clone http://github.com/bulletmark/cdhist
cd cdhist
sudo make uninstall # Do this to make sure old versions are purged
sudo make install
```

### CONFIGURATION

Each user who wants to use the cdhist facility should source the
`/etc/cdhist.bashrc` file into their bashrc, i.e in `~/.bashrc`
just add:

```
if [ -f /etc/cdhist.bashrc]; then
    source /etc/cdhist.bashrc
fi
```

Then log out and back in again.

### ALTERNATIVE COMMAND NAME

Some people may prefer not to alias their system `cd` command to this
utility and just use an alternative unique command name. To do this, set
`CDHISTCOMMAND` to your preferred name before you invoke the
`cdhist.bashrc` script in your `~/.bashrc`. E.g, to use the command name
`xd` rather than `cd`:

```
if [ -f /etc/cdhist.bashrc]; then
    export CDHISTCOMMAND=xd
    source /etc/cdhist.bashrc
fi
```

Then just type `xd /tmp` to change dir, `xd --` to see and select dirs,
etc.

### UPGRADE

```
cd cdhist  # Source dir, as above
git pull
sudo make install
```

### REMOVAL

```
cd cdhist  # Source dir, as above
sudo make uninstall
```

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
