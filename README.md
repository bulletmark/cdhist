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
directories.

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
source <(cdhist -i "cd -am 100")
```

The above sets `-a/--purge-always` and `-m/--size 100` options as defaults
for your `cd` command.

The following options are sensible candidates to set as default options:
`-m/--size`, `-a/--purge-always`, `-u/--no-user`, `-F/--fuzzy`.

Note if you set `-u/--no-user` options as default then option `-U/--user` exist
to allow you to temporarily override those defaults via the command line.

### Fuzzy Finder Integration

Any of the popular command line fuzzy search finders such as
[`fzf`][fzf], [`sk`][skim], [`tv`][television], or [`fzy`][fzy]
can be used with `cdhist`.

E.g. to use [`fzf`][fzf]:

```sh
source <(cdhist -i "cd -F fzf")
```

Now when you type `cd --` you will be prompted with a list of directories via
your fuzzy finder so you can search for a directory to select by fuzzy text
matching.

Or, to use [`fzf`][fzf] with preview of directory contents using [`eza`][eza]:

```sh
source <(cdhist -i "cd -uF \"fzf --preview 'eza --color=always -lF {} 2>/dev/null'\"")
```

Note that [`fzf`][fzf] will be used in the following description as it is by far
the most popular fuzzy finder and the one used by the author. When you set up
`fzf` [shell integration](https://junegunn.github.io/fzf/shell-integration/)
then you can use the following terminal key bindings for `fzf`:

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

[`cdhist.yazi`][cdhist.yazi] is a [yazi] plugin that provides cdhist
functionality within the [yazi] terminal file manager.

### GIT Worktree Integration

The `cdhist` utility previously provided an option to switch between [`git
worktree`][worktree] directories. However, this functionality has been removed
in August 2026 (at version 4.6) since the author has developed a much better
dedicated utility [`worktree-aid`] which users are encouraged to use instead.
[`worktree-aid`] (as shell function/alias `wt`) can be used in parallel and in
concert with `cdhist` to provide a more comprehensive solution for switching
between, adding, and removing [git worktrees][worktree].

## Usage

Type `cd -h` to view the usage summary:

```
usage: cd [-h] [-i] [-l] [-m SIZE] [-n NUM_LINES] [-p] [-a] [-U] [-u]
              [-F FUZZY] [-L] [-P] [-V]
              [directory]

A Linux shell directory stack "cd history" function.

positional arguments:
  directory             directory to cd to, or "--" to list history and
                        prompt, or "-n" for n'th entry in list or "-/<string>"
                        to match for "string" in dir

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
  -U, --no-user         do not substitute "~" for home directory
  -u                    toggle -U/--no-user option for one-off command only
  -F, --fuzzy FUZZY     use specified fuzzy finder program to select directory
                        from list
  -L, --follow-links    follow symbolic links (default=true)
  -P, --follow-physical
                        follow links to physical directory
  -V, --version         just output cd version
```

## Limitations

Regular `cd`, e.g. as provided by the bash builtin, offers some esoteric
command line options such as `-e` and `-@`, and shell options such as `autocd`,
`cdspell`, `cdable_vars`. These rarely used options are not supported by
cdhist.

## License

GPL-3.0-or-later.

[pipx]: https://github.com/pypa/pipx
[pipxu]: https://github.com/bulletmark/pipxu
[uvtool]: https://docs.astral.sh/uv/guides/tools/#installing-tools
[fzf]: https://github.com/junegunn/fzf
[fzy]: https://github.com/jhawthorn/fzy
[skim]: https://github.com/skim-rs/skim
[television]: https://github.com/alexpasmantier/television
[cdhist.yazi]: https://github.com/bulletmark/cdhist.yazi
[Yazi]: https://yazi-rs.github.io/
[eza]: https://github.com/eza-community/eza
[worktree]: https://git-scm.com/docs/git-worktree
[`worktree-aid`]: https://github.com/bulletmark/worktree-aid
