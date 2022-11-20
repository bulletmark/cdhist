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

    num = args.num_lines

    if 0 <= num < len(dirlist):
        dirlist = dirlist[:num] if reverse else dirlist[len(dirlist) - num:]
    else:
        num = len(dirlist)

    # List the worktrees
    for x, line in enumerate(reversed(dirlist) if reverse else dirlist, 1):
        n = num - x
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

def check_search(arg, dirlist, *, list_is_paths=False):
    'Search for arg in given dirlist'
    from itertools import count

    if not list_is_paths:
        dirlist = [Path(p) for p in dirlist]

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
                    elif not match_any:
                        if arg in name:
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

# vim: se et:
