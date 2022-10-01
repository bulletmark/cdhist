#!/usr/bin/env python3
'Misc utility functions for cdhist'
import sys
from pathlib import Path

HOME = Path('~').expanduser()
HOMESTR = str(HOME)

def unexpanduser(path):
    'Return string path with $HOME in string path substituted with ~'
    if path.startswith(HOMESTR):
        path = path.replace(HOMESTR, '~', 1)
    return path

def prompt(args, dirlist, *, reverse=False):
    'Present list of dirs to user and prompt for selection'
    if not dirlist:
        sys.exit('fatal: no directories')

    tty = open('/dev/tty', 'w')

    # List the worktrees
    size = len(dirlist)
    for x, line in enumerate(reversed(dirlist) if reverse else dirlist, 1):
        n = size - x
        tty.write(f'{n:3} {line}\n')

    if args.list:
        return None

    # Prompt for index
    tty.write('Select index [or <enter> to quit]: ')
    tty.flush()
    try:
        ans = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        return None

    return ans

def check_digit(arg, dirlist, *, reverse=False):
    'Check if arg is number and then return indexed entry in dirlist'
    if not arg.isdigit():
        return None

    num = int(arg)
    if num < 0 or num >= len(dirlist):
        sys.exit(f'Index "{num}" out of range.')

    if not reverse:
        num = len(dirlist) - num - 1

    return Path(dirlist[num])

def check_search(arg, dirlist):
    'Search for arg in given dirlist'
    for pathstr in dirlist:
        if arg in pathstr:
            return Path(pathstr)

    sys.exit(f'No directory matches "{arg}".')

# vim: se et:
