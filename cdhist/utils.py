#!/usr/bin/env python3
'Misc utility functions for cdhist'
from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path

HOME = Path.home()

def unexpanduser(path: str | Path) -> str:
    'Return path name, with $HOME replaced by ~ (opposite of Path.expanduser())'
    ppath = Path(path)

    if ppath.parts[:len(HOME.parts)] != HOME.parts:
        return str(path)

    return str(Path('~', *ppath.parts[len(HOME.parts):]))

def prompt(args: Namespace, dirlist: list[str], *,
           reverse: bool = False) -> str | None:
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

def check_digit(arg: str, dirlist: list[str], *, reverse: bool = False):
    'Check if arg is number and then return indexed entry in dirlist'
    if not arg.isdigit():
        return None

    num = int(arg)
    if num < 0 or num >= len(dirlist):
        sys.exit(f'Index "{num}" out of range.')

    if not reverse:
        num = len(dirlist) - num - 1

    return Path(dirlist[num])

def check_search(arg: str, dirlist: list[Path]) -> Path | None:
    'Search for arg in given dirlist'
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

    return None
