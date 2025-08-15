## CDHIST - Linux Directory History
[![PyPi](https://img.shields.io/pypi/v/cdhist)](https://pypi.org/project/cdhist/)
[![AUR](https://img.shields.io/aur/version/cdhist)](https://aur.archlinux.org/packages/cdhist/)

[cdhist](http://github.com/bulletmark/cdhist) is a utility which provides a
Linux shell **cd history** directory stack. A shell `cd` wrapper function calls
cdhist to intercept your typed `cd` command and maintain an ordered stack of
all directories you have previously visited which can be listed and quickly
navigated to.

[cdhist](http://github.com/bulletmark/cdhist) can also be used with a fuzzy
finder (such as [`fzf`][fzf]) to fuzzy search and select on previously visited
directories, and can be used to easily `cd` between [`git
worktree`](https://git-scm.com/docs/git-worktree) directories. See the sections
below about [Fuzzy Finder Integration](#fuzzy-finder-integration) and [Git
Worktree Integration](#git-worktree-integration).

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

That's it! The above is all you really need to know. Instead of having to type
the directory name you merely enter it's index. The directories are displayed
most recently visited last, without duplicates. Index 0 is the current
directory, index 1 is the previous, index 2 is the second previous, up to a
user configurable number (default 200).

If you prefer a more modern approach you can use a fuzzy finder such as
[`fzf`][fzf], [`sk`][skim], [`tv`][television], or [`fzy`][fzy]
to show and select from the list, instead of a simple index prompt. See the
section on [Fuzzy Finder Integration](#fuzzy-finder-integration) below.

Other available commands and options are:

List the current stack and its indices (without prompting):

```sh
$ cd -l
```

Change immediately to directory corresponding to stack index 4:

```sh
$ cd -4
```

Note that `cd -1` is equivalent to the native `cd -` for the previous
directory, `cd -2` is the directory before that, etc.

Search back through stack for directory containing "string" in it's name and
`cd` there:

```sh
$ cd -/string
```

Note, you can also type the text `string` at the `cd --` prompt to search, although for
frequent searching it is probably better to use an [integrated fuzzy
finder](#fuzzy-finder-integration).

Show help/usage:

```sh
$ cd -h
```

## Installation

Arch users can install [cdhist from the
AUR](https://aur.archlinux.org/packages/cdhist/) and skip to the next section.

Python 3.8 or later is required. Note [cdhist is on
PyPI](https://pypi.org/project/cdhist/) so the easiest way to install it is to
use [`uv tool`][uvtool] (or [`pipx`][pipx] or [`pipxu`][pipxu]).

```sh
$ uv tool install cdhist
```

To upgrade:

```sh
$ uv tool upgrade cdhist
```

To uninstall:

```sh
$ uv tool uninstall cdhist
```

## Setup

A user who wants to use the cdhist facility should add the following line to
their `~/.bashrc` or `~/.zshrc` file. Ensure it is added after where your PATH
is set up so that the command `cdhist` can be found. This creates the `cd`
wrapper command in your interactive shell session as a tiny function.

```sh
source <(cdhist -i)
```

Then log out and back in again to activate the new `cd` function. Note assuming
a normal `.bashrc` environment, this will alias your `cd` command in your
interactive terminal session only. The remapped `cd` will not be invoked by any
programs or scripts you run, or for other users etc.

### Alternative Command Name

Some people may prefer not to alias their real `cd` command to this utility and
just use an alternative unique command name. To do this, simply add your
desired command name as the first argument to the `cdhist -i` option in your
shell initialization code. E.g, to use the command name `xd` rather than `cd`,
use the following in your `~/.bashrc` or `~/.zshrc` file:

```sh
source <(cdhist -i xd)
```

Then log out/in, and then use `xd /tmp` to change dir, `xd --` to see and
select directories, etc.

### Default Options

You can set default cdhist options by appending options in the shell
initialization code, e.g:

```sh
source <(cdhist -i "cd -arm 100")
```

The above sets `-a (--purge-always)`, '' `-r (--git-relative)`, and `-m
(--size) 100` options as defaults for your `cd` command.

Note you can use multiple source lines to define multiple commands. E.g. define
one alias for your `cd` command, and another alias for your git worktree
command (e.g. `wt`). Both can have different cdhist options.

The following options are sensible candidates to set as default options:
`-m/--size`, `-a/--purge-always`, `-g/--git`, `-r/--git-relative`,
`-u/--no-user`, `-F/--fuzzy`, `-G/--no-fuzzy-git`.

Note if you set `-r/--git-relative` or `-u/--no-user` options as default then
options `-R/--no-git-relative` and `-U/--user` exist to allow you to
temporarily override those defaults via the command line.

### Fuzzy Finder Integration

Any of the popular command line fuzzy search finders such as
[`fzf`][fzf], [`sk`][skim], [`tv`][television], or [`fzy`][fzy]
can be used with `cdhist`.

E.g. to use [`fzf`][fzf]:

```sh
source <(cdhist -i "cd -F fzf")
```

Or, to use [`television`][television] with [`exa`][exa] to show a preview of
directory contents:

```sh
source <(cdhist -i "cd -uF \"tv --preview 'exa --color=always -l@F=always {}'\"")
```

Now when you type `cd --` you will be prompted with a list of directories via
your fuzzy finder so you can search for a directory to select by fuzzy text
matching.

Note if you use [`television`][television] then it is suggested to set the
`television` option `input_bar_position = bottom` in the `ui` section of your
[`~/.config/television/config.toml`](https://github.com/alexpasmantier/television/blob/main/.config/config.toml)
file so that the input bar is at the bottom of the screen and close where your
terminal prompt usually is.

In the following description, [`fzf`][fzf] will be used as it is by far the
most popular fuzzy finder and the one used by the author. When you set up `fzf`
[shell integration](https://junegunn.github.io/fzf/shell-integration/) then you
can use the following terminal key bindings for `fzf`:

- `CTRL+t` to select files,
- `CTRL+r` to select commands,
- `ATL+c` to select directories.

However, I never use the last `ATL+c` function because it lists directories
only under the current directory whereas I am much more interested in listing
all directories I have previously visited, i.e. those maintained by cdhist. So
I disable that function in `fzf` by setting the `FZF_ALT_C_COMMAND` to an empty
string before I source `fzf` in my `.bashrc` when [setting `fzf` up](https://junegunn.github.io/fzf/shell-integration/#setting-up-shell-integration).

Then I set the following shell key binding in my `~/.inputrc` file (need to
restart your login shell/terminal to activate):

```sh
"\ec": "cd --\n"
```

Now pressing `ALT+c` invokes cdhist to bring up the `fzf` list of my previously
visited directories. Alternately, use `ALT+d` for cdhist and keep `ALT+c` for
the default `fzf` search behavior.

You also have the choice of keeping the standard `cd --` command to work with
simple index selection, and map a different cdhist command name to use with
`ALT+c` only for the fuzzy finder. To do this, add the following 2 lines to your
`~/.bashrc` or `~/.zshrc` file:

```sh
source <(cdhist -i)
source <(cdhist -i "cdfuzzy -F fzf")
```

And then in your `~/.inputrc`:

```
"\ec": "cdfuzzy --\n"
```

Note all the above assumes you have the fuzzy finder somewhere in your PATH. If
you don't then just specify the full path, e.g:

```sh
source <(cdhist -i "cd -F /path-to/fzf")
```

### Yazi Integration

[`cdhist.yazi`][cdhist.yazi] is a [Yazi][yazi] plugin that provides cdhist
functionality within the [Yazi][yazi] terminal file manager.

### GIT Worktree Integration

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
/home/mark/src/myprog       f76b8e0 [main]
/home/mark/src/development  9796714 [development]
/home/mark/src/milestone1   bc921b8 [milestone1]
/home/mark/src/test         e6d965a [test]

# Alternately, use cdhist to list worktrees and choose one to navigate to:
$ cd -g
  3 ~/src/development 9796714 [development]
  2 ~/src/milestone1  bc921b8 [milestone1]
  1 ~/src/test        e6d965a [test]
  0 ~/src/myprog      f76b8e0 [main]
Select index [or <enter> to quit]: 2

$ pwd
/home/mark/src/milestone1

# Or, use cdhist to navigate to worktree dir for given branch name or
# commit:
$ cd -g main
$ pwd
/home/mark/src/myprog
```

Instead of having to type the full git repository directory name you merely are
prompted with a list and enter it's index. Or just directly enter the branch
name (or commit hash). The directories are displayed in the same order as the
output of the `git worktree list` command, except that the git directory
corresponding to the current working directory is shown first (index 0)
consistent with how the current directory is shown at index 0 for normal cd
history and thus conveniently showing you which git worktree you are currently
in which `git worktree list` unfortunately does not show.

In you enter text instead of an index, you only need to enter as much of the
branch name, or commit hash, as needed to be unique. Note that `cd -g` nicely
presents paths based from your HOME directory with a tilde (`~`) unlike the
longer full path displayed by `git worktree list` (although you can disable
that with the `-u/--no-user` option, likely set as a [default
option](#default-options)).

Note if you have `-F/--fuzzy` enabled but you don't want to also use that for
git worktree selection then you can disable it with the `-G/--no-fuzzy-git`
option.

#### Relative Git Worktree Directories

The `git worktree list` command displays absolute directory paths, and cdhist
does also by default, but many users prefer them displayed as shorter relative
paths. The Git worktree command does not provide this but you can enable it in
cdhist by adding the `-r/--git-relative` option, e.g:

```sh
$ cd -gr
  3 ../development 9796714 [development]
  2 ../milestone1  bc921b8 [milestone1]
  1 ../test        e6d965a [test]
  0 .              f76b8e0 [main]
Select index [or <enter> to quit]:
```

Most likely you will want to set this as your default so do that by adding
`-r/--git-relative` as a [default option](#default-options).

#### Git Worktree Functionality Alone

Some users may want the git worktree functionality provided by cdhist but are
not interested in the standard `cd` history functionality, or alternately, want
to use a completely separate command for the git worktree functionality. To do
this, simply add your desired command name and the git option the first
argument to the `cdhist` command in your shell initialization code. E.g, to use
the command name `wt` for git worktree functionality (only), add the following
in your `~/.bashrc` or `~/.zshrc` file:

```sh
source <(cdhist -i "wt -g")
```

Then log out/in. Type `wt` to list the git worktrees and be prompted to select
the directory etc. Of course, you can define this `wt` command in parallel to
using cdhist for your `cd` command if you want.

## Command Line Usage

Type `cdhist -h` to view the usage summary:

```
usage: cdhist [-h] [-i] [-l] [-m SIZE] [-n NUM_LINES] [-p] [-a] [-g] [-r]
                   [-R] [-u] [-U] [-F FUZZY] [-G] [-L] [-P] [-V]
                   [directory]

A Linux shell directory stack "cd history" function.

positional arguments:
  directory             directory (or branch for git worktree) to cd to, or
                        "--" to list history and prompt, or "-n" for n'th
                        entry in list or "-/<string>" to match for "string" in
                        dir

options:
  -h, --help            show help/usage
  -i, --init            output shell initialization code. Optionally specify
                        alternative command name as argument, default="cd"
  -l, --list            just list directory history
  -m, --size SIZE       maximum size of directory history (default=200)
  -n, --num-lines NUM_LINES
                        limit output to specified number of lines
  -p, --purge           just purge non-existent directories from history
  -a, --purge-always    always purge non-existent directories every write
  -g, --git             show git worktree directories instead
  -r, --git-relative    show relative git worktree paths instead of absolute
  -R, --no-git-relative
                        do not show relative git worktree paths (default)
  -u, --no-user         do not substitute "~" for home directory
  -U, --user            do substitute "~" for home directory (default)
  -F, --fuzzy FUZZY     use specified fuzzy finder program to select directory
                        from list
  -G, --no-fuzzy-git    do not use fuzzy finder for git worktree selection
  -L, --follow-links    follow symbolic links (default=true)
  -P, --follow-physical
                        follow links to physical directory
  -V, --version         just output cdhist version
```

## Limitations

Regular `cd`, e.g. as provided by the bash builtin, offers some esoteric
command line options such as `-e` and `-@`, and shell options such as `autocd`,
`cdspell`, `cdable_vars`. These rarely used options are not supported by
cdhist.

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
Public License at <https://en.wikipedia.org/wiki/GNU_General_Public_License> for more details.

[pipx]: https://github.com/pypa/pipx
[pipxu]: https://github.com/bulletmark/pipxu
[uvtool]: https://docs.astral.sh/uv/guides/tools/#installing-tools
[fzf]: https://github.com/junegunn/fzf
[fzy]: https://github.com/jhawthorn/fzy
[skim]: https://github.com/skim-rs/skim
[television]: https://github.com/alexpasmantier/television
[cdhist.yazi]: https://github.com/bulletmark/cdhist.yazi
[yazi]: https://yazi-rs.github.io/
[exa]: https://github.com/ogham/exa
