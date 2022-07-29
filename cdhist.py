#!/usr/bin/env python3
'A Linux shell directory stack "cd history" function'
#
# Copyright (C) 2010 Mark Blakeney. This program is distributed under
# the terms of the GNU General Public License.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any
# later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License at <http://www.gnu.org/licenses/> for more
# details.
#
# See help text below and accompanying README.

import os
import sys

# Default size of history (CDHISTSIZE + 0). Can be overridden by setting
# this as an environment variable.
CDHISTSIZE = int(os.environ.get('CDHISTSIZE') or 50)

# Set the following True if you want your home dir ($HOME) substituted
# in the directory list as '~'. Else unset or set False, etc.
CDHISTTILDE = os.environ.get('CDHISTTILDE')
if CDHISTTILDE and not CDHISTTILDE.lower().startswith('true'):
    CDHISTTILDE = None

HELP = '''\
A simple "cd history" function which intercepts (or can replace) your
shell "cd" command to maintain a stack of directories visited.

Usage examples:
$cmd somepath   : Add "somepath" to your directory stack and cd there.
$cmd --         : List the stack and its indices then prompt for dir to select.
$cmd -/string   : Search back through stack for "string" and cd there.
$cmd -l         : List the current stack and its indices.
$cmd -n         : cd to stack index "n".
$cmd -p         : Purge non-existent directories from history.
$cmd -h|?       : Print this help.
All other arguments are passed on to the normal cd command.
Environment   : You have CDHISTSIZE=$size, CDHISTTILDE=$tilde.
'''

# Constants and definitions
HOME = os.path.expanduser('~')
CDHISTFILE = os.path.join(HOME, '.cd_history')

def writeHist(hist):
    'Write the passed history stack to the history file'
    # Ensure private history file
    os.umask(0o177)

    try:
        with open(CDHISTFILE, 'w') as fd:
            fd.write('\n'.join(hist) + '\n')
    except IOError:
        pass

def readHist():
    'Read the history stack from the history file'
    try:
        with open(CDHISTFILE) as fd:
            hist = [d.rstrip('\n') for d in fd]
    except IOError:
        # No file, assume empty history
        hist = []

    return hist

def fetchHist():
    'Update and return the current history stack'
    # Get current and prev dirs
    pwd = [os.environ.get('PWD') or os.getcwd()]
    if 'OLDPWD' in os.environ:
        pwd.append(os.environ['OLDPWD'])

    # Read the history stack from the file but always prepend the
    # current ($PWD) and previous ($OLDPWD, i,e ~-) directories for this
    # particular user terminal session to ensure the history is
    # consistent with the shell (so that $PWD and $OLDPWD match stack
    # index 0 and 1). The stack is always pruned of duplicate entries
    # except for the current and previous directories which may be the
    # same because the shell allows this so we must too. The stack will
    # accumulate all directories traversed across all coexisting
    # terminal sessions.
    hist = [d for d in readHist() if d not in pwd]

    # Return the stack, constraining its size
    return (pwd + hist)[:CDHISTSIZE]

def selectHist(hist, num):
    'Bounds check the entered index and select directory if in range'
    if num < 0 or num >= len(hist):
        print(f'cdhist: number {num} out of range', file=sys.stderr)
        return 1

    print(hist[num])
    return 0

def searchHist(hist, text):
    'Search back for text in stack and select directory if found'
    for dir in hist[1:]:
        if text in dir:
            print(dir)
            return 0

    print(f'cdhist: string "{text}" not found', file=sys.stderr)
    return 1

def main():
    'Main code'
    # Main returns a status code:
    # 0 = Directory written to stdout. Calling script should cd to that
    #     directory.
    # 1 = Error/message written to stderr (etc). Caller should just
    #     quit.

    # Intercept home case immediately
    if len(sys.argv) <= 1:
        print(HOME)
        return 0

    if sys.argv[1][0] == '-':
        # Look for and process cdhist option
        if len(sys.argv) == 2:
            arg = sys.argv[1]

            # Show path of rc file on this system
            if arg == '-s':
                stem = os.path.splitext(os.path.basename(sys.argv[0]))[0]
                print(os.path.join(sys.prefix, 'share', stem, (stem + '.rc')))
                return 0

            if arg in {'-h', '-?'}:
                # Just output help/usage
                from string import Template
                print(Template(HELP).substitute(
                    cmd=os.environ.get('CDHISTCOMMAND', 'cd'),
                    size=CDHISTSIZE, tilde=CDHISTTILDE).rstrip(),
                    file=sys.stderr)
                return 1

            # Fetch the current history
            hist = fetchHist()

            # This may be a call to just update the directory history. I.e
            # after a successfull shell 'cd'.
            if arg == '-u':
                writeHist(hist)
                return 0

            # Just clean out the directory history?
            if arg == '-p':
                writeHist(h for h in hist if os.path.exists(h))
                return 0

            # List directory stack?
            if arg in {'--', '-l'}:
                tty = open('/dev/tty', 'w')

                # List the directory stack (in reversed output)
                for n, dird in reversed(list(enumerate(hist))):
                    if CDHISTTILDE and dird.startswith(HOME):
                        dird = dird.replace(HOME, '~', 1)

                    tty.write(f'{n:3} {dird}\n')

                if arg == '-l':
                    return 1

                # Prompt for index from the screen
                tty.write('Select directory index [or <enter> to quit]: ')
                tty.flush()
                try:
                    line = sys.stdin.readline().strip()
                except KeyboardInterrupt:
                    return 1

                if not line:
                    return 1

                # Select the index given by the user
                if line.isdigit():
                    return selectHist(hist, int(line))

                # Or, search for a string
                return searchHist(hist,
                        line[1:] if line[0] == '/' else line)

            if arg == '-':
                # A normal shell can't cd to OLDPWD when it is not set (e.g.
                # just after login). But we may have more history so use it :)
                return selectHist(hist, 1)

            if len(arg) > 1:
                if arg[1:].isdigit():
                    # Select this directory index
                    return selectHist(hist, int(arg[1:], 10))

                if arg[:2] == '-/':
                    # Search stack for "string" and select that dir
                    return searchHist(hist, arg[2:])

        if sys.argv[1] == '--':
            del sys.argv[1]
        else:
            print('cdhist: invalid option', file=sys.stderr)
            return 1

    # Fall through to real 'cd' to deal with normal dir
    print(' '.join(sys.argv[1:]))
    return 0

if __name__ == '__main__':
    sys.exit(main())

# vim: se et:
