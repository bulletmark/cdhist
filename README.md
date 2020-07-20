## BASH SHELL CD HISTORY

[cdhist](http://github.com/bulletmark/cdhist) is a utility which
provides a bash shell **cd history** directory stack. A bash `cd` alias
calls a tiny helper script to intercept your normal shell `cd` command
and maintain a stack of all directories you previously visited which can
be listed and quickly jumped to by numeric index.

The latest version and documentation is available at
http://github.com/bulletmark/cdhist.

### USAGE

Use the `cd` command to change directory as normal:

```
$ cd /tmp
$ cd /etc
$ cd /usr/share/doc
$ cd /boot/loader
$ cd ~/etc
$ cd
```

At any point you can use the `cd --` command to list all your previous
directories and be prompted for one to select and cd to:

```
$ cd --
  6 ...
  5 /tmp
  4 /etc
  3 /usr/share/doc
  2 /boot/loader
  1 ~/etc
  0 ~
Select directory index [or <enter> to quit]: 3
$ pwd
/usr/share/doc
```

That's it! The above is all you really need to know. Instead of having
to type the directory name you merely enter it's index. The directories
are displayed most recently visited last, without duplicates. Index 0 is
the current directory, index 1 is the previous, index 2 is the second
previous, up to a user configured number (default 30). Other available
commands and options are:

List the current stack and its indices (without prompting):

```
$ cd -l
```

Change dir to stack index "n":

```
$ cd -n
```

Search back through stack for "string" and cd there:

```
$ cd -/string
```

Note, you can also type `/string` at the `cd --` prompt to search.

Show this help:

```
$ cd -h|?
```

All other arguments are passed on to the normal cd command.

### INSTALLATION

Arch users can install [cdhist from the
AUR](https://aur.archlinux.org/packages/cdhist/) and skip to the next
section.

Ensure `python-pip` is installed. Bash and python 3.4 or later are
required.

Note [cdhist is on PyPI](https://pypi.org/project/cdhist/) so you can
just type `sudo pip3 install cdhist`. Or do the following to install
from this repository:

```
$ git clone http://github.com/bulletmark/cdhist
$ cd cdhist
$ sudo pip3 install .
```

### CONFIGURATION

Each user who wants to use the cdhist facility should source the
`cdhist.bashrc` file into their bashrc, i.e in `~/.bashrc`
just add the following lines:

```
for _d in /usr/share /usr/local/share; do
    _f="$_d/cdhist/cdhist.bashrc"
    if [[ -r $_f ]]; then
	source $_f
	break
    fi
done
```

Then log out and back in again.

### ALTERNATIVE COMMAND NAME

Some people may prefer not to alias their system `cd` command to this
utility and just use an alternative unique command name. To do this, set
`CDHISTCOMMAND` to your preferred name before you invoke the
`cdhist.bashrc` script in your `~/.bashrc`. E.g, to use the command name
`xd` rather than `cd` add the following export after the `if` test and
before the `source` line in the above.

```
export CDHISTCOMMAND=xd
```

Log out/in, and then just type `xd /tmp` to change dir, `xd --` to see
and select dirs, etc.

### UPGRADE

```
$ cd cdhist  # Source dir, as above
$ git pull
$ sudo pip3 install -U .
```

### REMOVAL

```
$ sudo pip3 uninstall cdhist
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
