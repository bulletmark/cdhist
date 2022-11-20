#!/usr/bin/python3
'A Linux shell directory stack "cd history" function.'
import os
import sys
import argparse
import shlex
import re
from pathlib import Path

from . import utils

# Following is template for the shell code injected into your session
SHELLCODE = '''
!cmd() {
    local d
    d=$(!prog "$@")

    if [ $? -ne 0 ]; then
        return 0
    fi

    builtin cd -- "$d"
}
'''

# Following is default installed command name but you can change it
# using a command line option
DEFCMD = 'cd'

PROG = Path(sys.argv[0]).stem.replace('_', '-')
CNFFILE = Path(os.getenv('XDG_CONFIG_HOME', '~/.config'), f'{PROG}-flags.conf')
CDHISTFILE = utils.HOME / '.cd_history'

def init_code(args):
    'Return shell init code as string'
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

def write_cd_hist(hist):
    'Write the passed history stack to the history file'
    # Ensure private history file
    os.umask(0o177)

    try:
        CDHISTFILE.write_text('\n'.join(hist) + '\n')
    except Exception:
        pass

def fetch_cd_hist(args):
    'Fetch the current history stack'
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
    hist = dict.fromkeys(hist.splitlines(keepends=False))
    pwd = os.getenv('PWD') or os.getcwd()
    oldpwd = os.getenv('OLDPWD')

    pwdlist = [path for path in (pwd, oldpwd) if path]
    for path in pwdlist:
        hist.pop(path, None)

    return (pwdlist + list(hist))[:args.size]

def parse_args_cd(args, hist):
    'Parse arguments for the cd command'
    if args.list or sys.argv[-1] == '--':
        hist_u = hist if args.no_user else \
                [utils.unexpanduser(d) for d in hist]
        arg = utils.prompt(args, hist_u, reverse=True)
        if not arg:
            return None

        path = utils.check_digit(arg, hist, reverse=True) or \
                utils.check_search(arg.lstrip('/'), hist)

    elif args.directory:
        path = None
        pathstr = args.directory
        if pathstr[0] == '-':
            if len(pathstr) == 1:
                # A normal shell can't cd to OLDPWD when it is not set (e.g.
                # just after login). But we have non-volatile history so
                # may as well use it :)
                path = Path(hist[1])
            else:
                path = utils.check_digit(pathstr[1:], hist, reverse=True)

        if not path:
            path = Path(pathstr)
    elif args.search:
        path = utils.check_search(args.search, hist)
    else:
        path = utils.HOME

    return path

def main():
    'Main code'
    # Main returns a status code:
    # 0 = Directory written to stdout. Calling script should cd to that
    #     worktree directory.
    # 1 = Error/message written to stderr (etc). Caller should just
    #     quit.

    # Parse arguments
    opt = argparse.ArgumentParser(description=__doc__.strip(), add_help=False,
            epilog=f'Note you can set default options in {CNFFILE}.')
    opt.add_argument('-i', '--init', action='store_true',
                     help='output shell initialization code. Optionally '
                     'specify alternative command name as argument, '
                     f'default="{DEFCMD}"')
    opt.add_argument('-s', '--shell', action='store_true',
                     help=argparse.SUPPRESS)
    opt.add_argument('-h', '--help', action='store_true',
                     help='show help/usage')
    opt.add_argument('-p', '--purge', action='store_true',
                     help='just purge non-existent directories from history')
    opt.add_argument('-a', '--purge-always', action='store_true',
                     help='always purge non-existent directories every write')
    opt.add_argument('-g', '--git', action='store_true',
                     help='show git worktree directories instead')
    opt.add_argument('-r', '--git-relative', action='store_true',
                     help='show relative git worktree paths instead '
                     'of absolute')
    opt.add_argument('-u', '--no-user', action='store_true',
                     help='do not substitute "~" for home directory')
    opt.add_argument('-l', '--list', action='store_true',
                     help='just list directory history')
    opt.add_argument('-m', '--size', type=int, default=50,
                     help='maximum size of directory history '
                     '(default=%(default)s)')
    opt.add_argument('-n', '--num-lines', type=int, default=-1,
                     help='limit output to specified number of lines')
    opt.add_argument('-L', '--follow-links', action='store_false',
                     dest='follow_physical',
                     help='follow symbolic links (default=true)')
    opt.add_argument('-P', '--follow-physical', action='store_true',
                     help='follow links to physical directory')
    opt.add_argument('directory', nargs='?', help='directory (or '
                     'branch for git worktree) to cd to, '
                     'or "--" to list history and prompt, '
                     'or "-n" for n\'th entry in list '
                     'or "-/<string>" to match for "string" in dir')

    # Argparse will not allow "-/search" so we fudge it before arg parsing
    if sys.argv[-1].startswith('-/'):
        search = sys.argv[-1][2:]
        del sys.argv[-1]
    else:
        search = None

    # Merge in default args from user config file. Then parse the
    # command line.
    cnffile = CNFFILE.expanduser()
    try:
        with cnffile.open() as fp:
            cnflines = [re.sub(r'#.*$', '', line).strip() for line in fp]
    except FileNotFoundError:
        cnflines = ''
    else:
        cnflines = ' '.join(cnflines).strip()

    args = opt.parse_args(shlex.split(cnflines) + sys.argv[1:])

    if args.help:
        return opt.format_help().strip()

    # Just output shell init code if asked
    if args.init:
        print(init_code(args))
        return

    # This is temporary back-compatibility code until the previously
    # provided but now depreciated -s/--shell option is removed. All
    # users should migrate to the above args.init option.
    if args.shell:
        uid = os.getuid()
        tmpdir = Path(f'/run/user/{uid}')
        shfile = tmpdir.joinpath(f'{PROG}.rc') if tmpdir.is_dir() \
                else Path(f'/tmp/{PROG}-{uid}.rc')
        shfile.write_text(init_code(args) + '\n')
        print(shfile)
        return

    hist = fetch_cd_hist(args)

    if args.purge:
        newhist = [p for p in hist if os.path.exists(p)]
        write_cd_hist(newhist[:args.size])
        return

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

    path = str(path)
    newhist = [path] + [p for p in hist if p != path]

    if args.purge_always:
        newhist = [p for p in newhist if os.path.exists(p)]

    write_cd_hist(newhist[:args.size])
    print(path)

if __name__ == '__main__':
    sys.exit(main())

# vim: se et:
