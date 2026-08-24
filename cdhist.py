'A Linux shell directory stack "cd history" function.'

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from argparse import SUPPRESS, ArgumentParser, Namespace
from contextlib import suppress
from pathlib import Path

HOME = Path.home()

# Following is default installed command name but you can change it
# using a command line option
DEFCMD = 'cd'

PROG = Path(__file__).stem
ENVVAR = '_' + PROG.upper()
CDHISTFILE = HOME / '.cd_history'

# Following is template for the shell code injected into your session
SHELLCODE = """
!cmd() {
    local !envvar=""
    export !envvar
    !envvar=$(!prog "$@")
    local r=$?

    if [ $r -ne 0 ]; then
        if [ $r -eq 2 ]; then
            return 0
        fi
        return $r
    fi

    builtin cd -- "$!envvar"
}
"""


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

    return CTemplate(SHELLCODE.strip()).substitute(envvar=ENVVAR, cmd=cmd, prog=prog)


class Xargs:
    """
    Class to process the special case of the last argument being a cd history
    selector: "cd -", "cd --", "cd -/string", or "cd -n". We process this and
    remove it before passing the remaining regular arguments to argparse.
    """

    def __init__(self) -> None:
        self.previous = False
        self.prompt = False
        self.search = ''
        self.number = ''

        if len(argv := sys.argv) < 2:
            return

        last_arg = argv[-1]

        if last_arg[0] != '-':
            return
        elif len(last_arg) == 1:
            self.previous = True
        elif (rest := last_arg[1:]) == '-':
            self.prompt = True
        elif rest[0] == '/':
            self.search = rest[1:]
        elif rest.isdigit():
            self.number = rest
        else:
            return

        del argv[-1]


def unexpanduser(path: str | Path) -> str:
    "Return path name, with $HOME replaced by ~ (opposite of Path.expanduser())"
    ppath = Path(path)

    if ppath.parts[: len(HOME.parts)] != HOME.parts:
        return str(path)

    return str(Path('~', *ppath.parts[len(HOME.parts) :]))


def fuzzy_prompt(args: Namespace, dirlist: list[str]) -> str | None:
    try:
        res = subprocess.run(
            shlex.split(args.fuzzy),
            input='\n'.join(dirlist),
            stdout=subprocess.PIPE,
            text=True,
        )
    except Exception as e:
        sys.exit(f'Error running fuzzy finder: {e}')

    return res.stdout.strip() if res.returncode == 0 else None


def prompt(args: Namespace, dirlist: list[str]) -> str | None:
    "Present list of dirs to user and prompt for selection"
    if not dirlist:
        sys.exit('fatal: no directories')

    num = args.num_lines

    if 0 <= num < len(dirlist):
        dirlist = dirlist[:num]
    else:
        num = len(dirlist)

    # List the directories
    for x, line in enumerate(reversed(dirlist)):
        n = num - x - 1
        args._stdout.write(f'{n:3} {line}\n')

    if args.list:
        return None

    # Prompt for index
    args._stdout.write('Select index [or <enter> to quit]: ')
    args._stdout.flush()
    try:
        ans = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        return None

    return ans


def check_digit(arg: str, dirlist: list[str]) -> Path | None:
    "Check if arg is number and then return indexed entry in dirlist"
    if not arg.isdigit():
        return None

    num = int(arg)
    if num < 0 or num >= len(dirlist):
        sys.exit(f'Index "{num}" out of range.')

    return Path(dirlist[num])


def check_search(arg: str, dirlist: list[Path]) -> Path | None:
    "Search for arg in given dirlist"
    from itertools import count

    # Perform a somewhat heuristic search. Iterate through all dirs and
    # look for match in final dir, then go up a level if no match and
    # iterate again. Always favor a full match then a partial start
    # match then a match anywhere.
    for level in count(1):
        complete = True
        match_start = match_any = None
        for path in dirlist:
            if len(path.parts) >= level:
                name = path.parts[-level]
                if name == arg:
                    return path

                complete = False
                if not match_start:
                    if name.startswith(arg):
                        match_start = path
                    elif not match_any and arg in name:
                        match_any = path

        # Did not find a full match at this level. If we found a partial
        # match at the start then return that, else if we found a match
        # anywhere then return that.
        if match_start:
            return match_start
        elif match_any:
            return match_any

        if complete:
            sys.exit(f'No match on "{arg}".')


def write_cd_hist(hist: list[str], maxsize: int, purge: bool) -> None:
    "Write the passed history stack to the history file"
    # Ensure private history file
    os.umask(0o177)

    if purge:
        hist = [p for p in hist if os.path.exists(p)]

    with suppress(Exception):
        CDHISTFILE.write_text('\n'.join(hist[:maxsize]) + '\n')


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
    if args.xargs.previous:
        # A normal shell can't cd to OLDPWD when it is not set (e.g.
        # just after login). But we have non-volatile history so
        # may as well use it :)
        path = Path(hist[1]) if len(hist) > 1 else Path('-')
    elif arg := args.xargs.number:
        path = check_digit(arg, hist)
    elif arg := args.xargs.search:
        path = check_search(arg, [Path(d) for d in hist])
    elif args.list or args.xargs.prompt:
        hist_u = hist if args.no_user else [unexpanduser(d) for d in hist]
        if args.fuzzy and not args.list:
            # We don't car about maintaining $PWD as index 0 and $OLDPWD as index 1 in
            # fuzzy mode so can remove one if they are duplicates
            if len(hist) > 1 and hist[0] == hist[1]:
                hist_u = hist_u[1:]

            if not (arg := fuzzy_prompt(args, hist_u)):
                return None

            path = Path(arg).expanduser()
        else:
            if not (arg := prompt(args, hist_u)):
                return None

            path = check_digit(arg, hist) or check_search(
                arg.lstrip('/'), [Path(d) for d in hist]
            )
    elif arg := args.directory:
        path = Path(arg)
    else:
        path = HOME

    return path


def main() -> int:
    "Main code"
    # Main returns a status code:
    # 0 = Directory written to stdout. Calling script should cd to that
    #     directory.
    # 1 = Error/message written to stderr via sys.exit(). Calling script should just
    #     quit with exit code 1.
    # 2 = Caller should silently quit and exit with code 0.

    # We need to determine if we are running in a shell function.
    # Also, Python 3.14 added color help/usage output but has a bug when
    # outputting to a device other than stdout, so we override auto-detection.
    # See https://github.com/python/cpython/issues/156144
    if (running_in_shell := ENVVAR in os.environ) and sys.version_info[:2] == (3, 14):
        os.environ['FORCE_COLOR'] = '1'

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
    opt.add_argument(
        '-l', '--list', action='store_true', help='just list directory history'
    )
    opt.add_argument(
        '-m',
        '--size',
        type=int,
        default=200,
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
        '-U',
        '--no-user',
        action='store_true',
        help='do not substitute "~" for home directory',
    )
    opt.add_argument(
        '-u',
        action='store_true',
        help='toggle -U/--no-user option for one-off command only',
    )
    opt.add_argument(
        '-F',
        '--fuzzy',
        help='use specified fuzzy finder program to select directory from list',
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
        '-V', '--version', action='store_true', help='show program version and exit'
    )
    opt.add_argument(
        '-h', '--help', action='store_true', help='show help message and exit'
    )
    opt.add_argument('-g', '--git', action='store_true', help=SUPPRESS)
    opt.add_argument('-_', action='store_true', help=SUPPRESS)
    opt.add_argument(
        'directory',
        nargs='?',
        help='directory to cd to, '
        'or "--" to list history and prompt, '
        'or "-n" for n\'th entry in list '
        'or "-/<string>" to match for "string" in dir',
    )

    # Preprocess and potentially remove the last argument
    xargs = Xargs()

    # Parse the rest of the arguments
    args = opt.parse_args()

    if args._:
        sys.exit('You need to log out and back in to your shell for new cdhist.')

    if args.u:
        args.no_user = not args.no_user

    if args.git:
        sys.exit(
            f'The -g/--git option for navigating git worktrees is no longer supported by {PROG}.\n'
            'Use https://github.com/bulletmark/worktree-aid instead.'
        )

    if running_in_shell:
        try:
            args._stdout = open('/dev/tty', 'w')
        except Exception as e:
            sys.exit(f'error: can not write to terminal in shell function mode: {e}')

        shell_return = 2
    else:
        args._stdout = sys.stdout
        shell_return = 0

    if args.help:
        opt.print_help(args._stdout)
        return shell_return

    if args.version:
        from importlib import metadata

        try:
            version = metadata.version(PROG)
        except Exception:
            version = '?'

        print(version, file=args._stdout)
        return shell_return

    # Just output shell init code if asked
    if args.init:
        if running_in_shell:
            sys.exit(f'Must invoke using "{PROG}" to output shell initialization code.')

        print(init_code(args))
        return shell_return

    hist = fetch_cd_hist(args)

    if args.purge:
        write_cd_hist(hist, args.size, True)
        return shell_return

    args.xargs = xargs
    if not (path := parse_args_cd(args, hist)):
        return shell_return

    # Ensure directory is valid before we try and cd to it
    if not path.exists():
        sys.exit(f'"{path}" does not exist.')
    if not path.is_dir():
        sys.exit(f'"{path}" is not a directory.')

    try:
        any(path.iterdir())
    except Exception:
        sys.exit(f'"{path}" is not accessible.')

    if args.follow_physical:
        try:
            path = path.resolve()
        except Exception:
            sys.exit(f'"{path}" can not be resolved.')

    pathstr = str(path)
    newhist = [pathstr] + [p for p in hist if p != pathstr]
    write_cd_hist(newhist, args.size, args.purge_always)
    print(pathstr)

    if running_in_shell:
        args._stdout.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
