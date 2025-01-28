#!/usr/bin/python3
'A Linux shell directory stack "cd history" function.'

from __future__ import annotations

import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from . import utils

# Following is template for the shell code injected into your session
SHELLCODE = """
!cmd() {
    local d
    d=$(!prog "$@")
    local r=$?

    if [ $r -ne 0 ]; then
        return $r
    fi

    builtin cd -- "$d"
}
"""

# Following is default installed command name but you can change it
# using a command line option
DEFCMD = 'cd'

PROG = Path(sys.argv[0]).stem
CDHISTFILE = utils.HOME / '.cd_history'


def init_code(args: Namespace) -> str:
    "Return shell init code as string"
    from string import Template

    # We need to change the template delimiter because the standard
    # delimiter "$" is too common in regular shell code .
    class CTemplate(Template):
        delimiter = '!'

    cmd = args.directory or DEFCMD
    prog = sys.argv[0]
    arglist = cmd.split(maxsplit=1)
    if len(arglist) > 1:
        cmd, opts = arglist
        prog += f' {opts}'

    return CTemplate(SHELLCODE.strip()).substitute(cmd=cmd, prog=prog)


def write_cd_hist(hist: list[str], maxsize: int, purge: bool) -> None:
    "Write the passed history stack to the history file"
    # Ensure private history file
    os.umask(0o177)

    if purge:
        hist = [p for p in hist if os.path.exists(p)]

    try:
        CDHISTFILE.write_text('\n'.join(hist[:maxsize]) + '\n')
    except Exception:
        pass


def fetch_cd_hist(args: Namespace) -> list[str]:
    "Fetch the current history stack"
    # Read the history stack from the file but always prepend the
    # current ($PWD) and previous ($OLDPWD, i,e ~-) directories for this
    # particular user terminal session to ensure the history is
    # consistent with the shell (so that $PWD and $OLDPWD match stack
    # index 0 and 1). The stack is always pruned of duplicate entries
    # except for the current and previous directories which may be the
    # same because the shell allows this so we must too. The stack will
    # accumulate all directories traversed across all coexisting
    # terminal sessions.
    try:
        hist = CDHISTFILE.read_text()
    except Exception:
        # No file, assume empty history
        hist = ''

    # Return the stack, removing duplicates and constraining the size
    histd = dict.fromkeys(hist.splitlines(keepends=False))
    pwd = os.getenv('PWD') or os.getcwd()
    oldpwd = os.getenv('OLDPWD')

    pwdlist = [path for path in (pwd, oldpwd) if path]
    for path in pwdlist:
        histd.pop(path, None)

    return (pwdlist + list(histd))[: args.size]


def parse_args_cd(args: Namespace, hist: list[str]) -> Path | None:
    "Parse arguments for the cd command"
    if args.list or sys.argv[-1] == '--':
        hist_u = hist if args.no_user else [utils.unexpanduser(d) for d in hist]
        arg = utils.prompt(args, hist_u, reverse=True)
        if not arg:
            return None

        path = utils.check_digit(arg, hist, reverse=True) or utils.check_search(
            arg.lstrip('/'), [Path(d) for d in hist]
        )

    elif args.directory:
        path = None
        pathstr = args.directory
        if pathstr[0] == '-':
            if len(pathstr) == 1 and len(hist) > 1:
                # A normal shell can't cd to OLDPWD when it is not set (e.g.
                # just after login). But we have non-volatile history so
                # may as well use it :)
                path = Path(hist[1])
            else:
                path = utils.check_digit(pathstr[1:], hist, reverse=True)

        if not path:
            path = Path(pathstr)
    elif args.search:
        path = utils.check_search(args.search, [Path(d) for d in hist])
    else:
        path = utils.HOME

    return path


def main() -> str | int | None:
    "Main code"
    # Main returns a status code:
    # 0 = Directory written to stdout. Calling script should cd to that
    #     worktree directory.
    # 1 = Error/message written to stderr (etc). Caller should just
    #     quit.

    # Parse arguments
    opt = ArgumentParser(description=__doc__, add_help=False)
    opt.add_argument(
        '-i',
        '--init',
        action='store_true',
        help='output shell initialization code. Optionally '
        'specify alternative command name as argument, '
        f'default="{DEFCMD}"',
    )
    opt.add_argument('-h', '--help', action='store_true', help='show help/usage')
    opt.add_argument(
        '-p',
        '--purge',
        action='store_true',
        help='just purge non-existent directories from history',
    )
    opt.add_argument(
        '-a',
        '--purge-always',
        action='store_true',
        help='always purge non-existent directories every write',
    )
    opt.add_argument(
        '-g', '--git', action='store_true', help='show git worktree directories instead'
    )
    opt.add_argument(
        '-r',
        '--git-relative',
        action='store_true',
        help='show relative git worktree paths instead of absolute',
    )
    opt.add_argument(
        '-R',
        '--no-git-relative',
        action='store_false',
        dest='git_relative',
        help='do not show relative git worktree paths (default)',
    )
    opt.add_argument(
        '-u',
        '--no-user',
        action='store_true',
        help='do not substitute "~" for home directory',
    )
    opt.add_argument(
        '-U',
        '--user',
        action='store_false',
        dest='no_user',
        help='do substitute "~" for home directory (default)',
    )
    opt.add_argument(
        '-l', '--list', action='store_true', help='just list directory history'
    )
    opt.add_argument(
        '-m',
        '--size',
        type=int,
        default=50,
        help='maximum size of directory history (default=%(default)s)',
    )
    opt.add_argument(
        '-n',
        '--num-lines',
        type=int,
        default=-1,
        help='limit output to specified number of lines',
    )
    opt.add_argument(
        '-L',
        '--follow-links',
        action='store_false',
        dest='follow_physical',
        help='follow symbolic links (default=true)',
    )
    opt.add_argument(
        '-P',
        '--follow-physical',
        action='store_true',
        help='follow links to physical directory',
    )
    opt.add_argument(
        '-V', '--version', action='store_true', help=f'just output {PROG} version'
    )
    opt.add_argument(
        'directory',
        nargs='?',
        help='directory (or '
        'branch for git worktree) to cd to, '
        'or "--" to list history and prompt, '
        'or "-n" for n\'th entry in list '
        'or "-/<string>" to match for "string" in dir',
    )

    # Argparse will not allow "-/search" so we fudge it before arg parsing
    if sys.argv[-1].startswith('-/'):
        search = sys.argv[-1][2:]
        del sys.argv[-1]
    else:
        search = None

    args = opt.parse_args()

    if args.help:
        return opt.format_help().strip()

    if args.version:
        from importlib import metadata

        pkg = Path(sys.argv[0]).stem.replace('-', '_')
        try:
            version = metadata.version(pkg)
        except Exception:
            version = '?'

        print(version)
        return None

    # Just output shell init code if asked
    if args.init:
        print(init_code(args))
        return None

    hist = fetch_cd_hist(args)

    if args.purge:
        write_cd_hist(hist, args.size, True)
        return None

    args.search = search

    if args.git:
        from . import git_worktree

        path = git_worktree.parse_args(args)
    else:
        path = parse_args_cd(args, hist)

    if not path:
        return 1

    # Ensure directory is valid before we try and cd to it
    if not path.exists():
        return f'"{path}" does not exist.'
    if not path.is_dir():
        return f'"{path}" is not a directory.'
    try:
        any(path.iterdir())
    except Exception:
        return f'"{path}" is not accessible.'

    if args.follow_physical:
        try:
            path = path.resolve()
        except Exception:
            return f'"{path}" can not be resolved.'

    pathstr = str(path)
    newhist = [pathstr] + [p for p in hist if p != pathstr]
    write_cd_hist(newhist, args.size, args.purge_always)
    print(pathstr)
    return None


if __name__ == '__main__':
    sys.exit(main())
