## Linux Directory History
[![PyPi](https://img.shields.io/pypi/v/cdhist)](https://pypi.org/project/cdhist/)
[![AUR](https://img.shields.io/aur/version/cdhist)](https://aur.archlinux.org/packages/cdhist/)

[cdhist](http://github.com/bulletmark/cdhist) is a utility which
provides a Linux shell **cd history** directory stack. A shell `cd`
wrapper function calls cdhist to intercept your typed `cd` command and
maintain an ordered stack of all directories you have previously visited
which can be listed and quickly navigated to.

[cdhist](http://github.com/bulletmark/cdhist) can also be used with the
[Command Line Fuzzy Finder](https://github.com/junegunn/fzf) `fzf` to
fuzzy search and select on previously visited directories, and can be
used to easily `cd` between [`git worktree`](https://git-scm.com/docs/git-worktree)
directories. See the sections below about [FZF
Integration](#fzf-integration) and [Git Worktree
Integration](#git-worktree-integration).

The latest version and documentation is available at
http://github.com/bulletmark/cdhist.

## Example Usage

Use the `cd` command to change directory as normal:

```sh
$ cd /tmp
$ cd /etc
$ cd /usr/share/doc
$ cd /boot/loader
$ cd ~/etc
$ cd
```

At any point you can use the `cd --` command to list all your previously
visited directories and be prompted for one to select and `cd` to:

```
$ cd --
  6 ...
  5 /tmp
  4 /etc
  3 /usr/share/doc
  2 /boot/loader
  1 ~/etc
  0 ~
Select index [or <enter> to quit]: 3
$ pwd
/usr/share/doc
```

That's it! The above is all you really need to know. Instead of having
to type the directory name you merely enter it's index. The directories
are displayed most recently visited last, without duplicates. Index 0 is
the current directory, index 1 is the previous, index 2 is the second
previous, up to a user configurable number (default 50). Other available
commands and options are:

List the current stack and its indices (without prompting):

```sh
$ cd -l
```

Change immediately to directory having stack index "n":

```sh
$ cd -n
```

Search back through stack for directory containing "string" and `cd`
there:

```sh
$ cd -/string
```

Note, you can also type `string` at the `cd --` prompt to search.

Show this help:

```sh
$ cd -h|?
```

## Installation

Arch users can install [cdhist from the
AUR](https://aur.archlinux.org/packages/cdhist/) and skip to the next
section.

Ensure `pip3` is installed. Python 3.7 or later is required.

Note [cdhist is on PyPI](https://pypi.org/project/cdhist/) so you can
just type `sudo pip3 install -U cdhist`. Or do the following to install
from this repository:

```sh
$ git clone http://github.com/bulletmark/cdhist
$ cd cdhist
$ sudo pip3 install -U .
```

## Setup

Each user who wants to use the cdhist facility should add the following
lines to their `~/.bashrc` or `~.zshrc` file (after where your PATH is
set up so that the command `cdhist` can be found). This creates the `cd`
wrapper command in your interactive shell session as a tiny function.
Note you can [customize the command name](#alternative-command-name) if
you want.

```sh
if type cdhist &>/dev/null; then
    . <(cdhist -i)
fi
```

Then log out and back in again.

## FZF Integration

The popular [Command Line Fuzzy Finder](https://github.com/junegunn/fzf)
`fzf` can easily be integrated with cdhist to provide fuzzy search
navigation over your directory history. Set the following in your
environment to have `fzf` search the directories recorded by cdhist:

```sh
export FZF_ALT_C_COMMAND="cat $HOME/.cd_history"
```

Since `fzf` version 0.31.0, you also should make a small change to the
way you source the `fzf` completion and key-binding files into your
shell, e.g. in your `~/.bashrc`. The following is a typical script to
load `fzf` except the source line must be changed to do an "on the
fly" edit of `builtin cd` to regular `cd`. E.g:

```sh
for _d in /usr/share/fzf /usr/share/fzf/shell /usr/share/doc/fzf/examples \
          /usr/share/bash-completion/completions/fzf ; do
    if [[ -d $_d ]]; then
        for _f in $_d/key-bindings.bash $_d/completion.bash; do
            if [[ -f $_f ]]; then
                . <(sed 's/builtin cd/cd/' $_f)
            fi
        done
    fi
done
```

After doing this (and reloading your shell session), you can use the
`fzf` key binding `<ALT+C>` to have `fzf` list all your previous
directories and fuzzy match on them for selection as you type. `fzf` can
also provide fancy [directory
previews](https://github.com/junegunn/fzf/wiki/Configuring-shell-key-bindings#preview-1)
using `tree`, etc. Of course the cdhist native command `cd --` and
other cdhist commands described above are still available, in addition
to the `fzf` key binding.

### Pruning Non-Existent Directories
If you prefer that directories that do not exist are excluded from `fzf`
and your `cd` history (i.e. exclude directories that have been deleted
since they were last visited), then you can define the `fzf` command as:

```sh
export FZF_ALT_C_COMMAND="cdhist -p && cat $HOME/.cd_history"
```

An alternative is to always exclude non-existent directories from your
cd history by setting the `--prune-always` as a [default
option](#default-options).

## Alternative Command Name

Some people may prefer not to alias their system `cd` command to this
utility and just use an alternative unique command name. To do this,
simply add your desired command name as an extra argument to the
`cdhist` command in your shell initialization code. E.g, to use the
command name `xd` rather than `cd`, use the following in
your `~/.bashrc` or `~.zshrc` file:

```sh
if type cdhist &>/dev/null; then
    . <(cdhist -i xd)
fi
```

Then log out/in, and then just type `xd /tmp` to change dir, `xd --` to see
and select directories, etc.

## GIT Worktree Integration

[cdhist](http://github.com/bulletmark/cdhist) can be used to easily `cd`
between [git worktree](https://git-scm.com/docs/git-worktree)
directories. You use the `cd -g` command to list all your worktrees and
be prompted for one to select, and then you will be switched to the
associated directory, and it will be added to your `cd` history.

```sh
# Current directory:
$ pwd
/home/mark/src/myprog

# List worktrees using standard git command:
$ git worktree list
/home/mark/src/myprog       cbbe856 [main]
/home/mark/src/development  a1bf827 [development]
/home/mark/src/milestone1   c40f826 [milestone1]
/home/mark/src/test         e2be219 [test]

# Alternately, usd cdhist to list worktrees and choose one to navigate to:
$ cd -g
  0 ~/src/myprog      cbbe856 [main]
  1 ~/src/development a1bf827 [development]
  2 ~/src/milestone1  c40f826 [milestone1]
  3 ~/src/test        e2be219 [test]
Select index [or <enter> to quit]: 2

$ pwd
/home/mark/src/milestone1

# Or, use cdhist to navigate to worktree dir for given branch name or
# commit:
$ cd -g main
$ pwd
/home/mark/src/myprog

```

Instead of having to type the full git repository directory name you
merely are prompted with a list and enter it's index. Or just directly
enter the branch name (or commit hash). The directories are displayed in
the same order as the output of the `git worktree list` command. You
only need to enter as much of the branch name, or commit hash, as needed
to be unique. Note that `cd -g` nicely presents paths based from your
HOME directory with a tilde (`~`) unlike the longer full path displayed
by `git worktree list` (although you can change that with the
`-u/--no-user` option, likely set as a [default
option](#default-options)).

### Relative Git Worktree Directories

The `git worktree list` command displays absolute directory paths, and
cdhist does also by default, but many users prefer them displayed
as relative paths. The Git worktree command does not provide this but
you can enable it in cdhist by adding the `-r/--relative` option, e.g:

```sh
$ cd -gr
  0 . cbbe856      [main]
  1 ../development a1bf827 [development]
  2 ../milestone1  c40f826 [milestone1]
  3 ../test        e2be219 [test]
Select index [or <enter> to quit]:
```

Most likely you will want to set this as your default so do that by
adding `--relative` as a [default option](#default-options).

### Git Worktree Functionality Alone

Some users may want the git worktree functionality provided by cdhist
but are not interested in the standard `cd` history functionality, or
alternately, want to use a completely separate command for the git
worktree functionality. To do this, simply add your desired command name
and the git option as an extra argument to the `cdhist` command in your
shell initialization code. E.g, to use the command name `wt` for git
worktree functionality (only), change/add the following in your
`~/.bashrc` or `~.zshrc` file:

```sh
if type cdhist &>/dev/null; then
    . <(cdhist -i "wt -g")
fi
```

Then log out/in, and then just type `wt` to list the git worktrees and
be prompted to select the directory etc. Of course, you can define this
`wt` command in parallel to using cdhist for your `cd` command if
you want.

## Default Options

There are 2 alternatives to set default cdhist options:

1. Set options in startup configuration file.
2. Set options in shell initialization code.

It's merely personal preference which you choose.

### Set Options in Startup Configuration File

You can add default options to a personal configuration file
`~/.config/cdhist-flags.conf`. If that file exists then each line in
the file will be concatenated and automatically prepended to your command
line options. The following options are sensible candidates to set as
default options: `--purge-always`, `--git-relative`, `--no-user`,
`--size`. Comments on any line are excluded.

You are best to use the full/long name for options and to add them on
individual lines in the file so they are easy to read and easy to
comment out temporarily etc.

### Set Options in Shell Initialization Code

Alternately, just set your preferred default options in your shell
initialization code, e.g:

```sh
if type cdhist &>/dev/null; then
    . <(cdhist -i "cd -arm 200")
fi
```

The above sets `-a (--purge-always)`, `-r (--git-relative)`, and
`-m (--size) 200` options as defaults for your `cd` command. Best to use
the short option names to keep the imported shell function definition
concise.

## Command Line Usage

Type `cdhist -h` to view the usage summary:

```
usage: cdhist [-i] [-h] [-p] [-a] [-g] [-r] [-u] [-l] [-m SIZE]
                   [-n NUM_LINES] [-L] [-P]
                   [directory]

A Linux shell directory stack "cd history" function.

positional arguments:
  directory             directory (or branch for git worktree) to cd to, or
                        "--" to list history and prompt, or "-n" for n'th
                        entry in list or "-/<string>" to match for "string" in
                        dir

options:
  -i, --init            output shell initialization code. Optionally specify
                        alternative command name as argument, default="cd"
  -h, --help            show help/usage
  -p, --purge           just purge non-existent directories from history
  -a, --purge-always    always purge non-existent directories every write
  -g, --git             show git worktree directories instead
  -r, --git-relative    show relative git worktree paths instead of absolute
  -u, --no-user         do not substitute "~" for home directory
  -l, --list            just list directory history
  -m SIZE, --size SIZE  maximum size of directory history (default=50)
  -n NUM_LINES, --num-lines NUM_LINES
                        limit output to specified number of lines
  -L, --follow-links    follow symbolic links (default=true)
  -P, --follow-physical
                        follow links to physical directory

Note you can set default options in ~/.config/cdhist-flags.conf.
```

## Limitations

Regular `cd`, e.g. as provided by the bash builtin, offers some esoteric
command line options such as `-e` and `-@`, and shell options such as
`autocd`, `cdspell`, `cdable_vars`. These rarely used options are not
supported by cdhist.

## Upgrade

```sh
$ cd cdhist  # Source dir, as above
$ git pull
$ sudo pip3 install -U .
```

## Removal

```sh
$ unset cd
$ sudo pip3 uninstall cdhist
```

## Major Version Change History

Version 3.0 changes and new features:

1. Added function to `cd` between [`git
worktrees`](https://git-scm.com/docs/git-worktree). Can configure this
as separate command if preferred, with option to display relative paths.

2. Cleaner installation using `-i` option so no need for separate
`cdhist.rc` file and can set arguments when installing to customise
command name + options etc.

3. Added `-L`/`-P` standard `cd` options.

4. Added `-a/--purge-always` option to always prune history.

5. Added ability to set default options in
`~/.config/cdhist-flags.conf`.

6. Parses options/arguments using standard Python argparse.

7. Let setuptools build the main program stub rather than install our
own.

8. Min Python version up from 3.4 to 3.7.

9. Now installed as a Python package (directory) rather than a module
(single file).

10. Some of these changes slow the program down but architecture is
changed so the program is run once only, not twice as it ran before.
Second run was to save the new directory after `cd` had validated it,
but now we validate it ourself before passing to `cd`. So net
performance is quicker than previous version, at least for the vanilla
case of changing directory. This is not noticeable on normal PC's but is
on constrained platforms like Raspberry Pi 2/3 using SD card.

11. If you were previously setting `CDHISTSIZE` or `CDHISTTILDE` settings
via environment variables then you now need to set them using `--size`
and `--no-user` in `~/.config/cdhist-flags.conf`.

12. The `-s` option to return a `cdhist.rc` file name for initialisation
is still currently supported for backwards-compatibility but is
undocumented and depreciated (a temporary file is created and returned).
It will likely eventually be removed.

## License

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
