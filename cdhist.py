#!/usr/bin/env python
'A bash directory stack "cd history" function'
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

# Make work with python 2 and 3
from __future__ import print_function
import os, sys

# Default size of history (CDHISTSIZE + 0). Can be overridden by setting
# this as an environment variable.
CDHISTSIZE = int(os.environ.get('CDHISTSIZE') or 31)

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
$cmd -l         : List the current stack and its indices.
$cmd -n         : cd to stack index "n".
$cmd -/string   : Search back through stack for REGEXP "string" and cd there.
$cmd --         : List the stack and its indices then prompt for dir to select.
$cmd -h|?       : Print this help.
All other arguments are passed on to the normal cd command.
Environment   : You have CDHISTSIZE=$size, CDHISTTILDE=$tilde.
'''

# Constants and definitions
HOME = os.path.expanduser('~')
CDHISTFILE = os.path.join(HOME, '.cd_history')

def writeHist(hist):
    'Write the passed history stack to the history file'
    try:
        with open(CDHISTFILE, 'w') as fd:
            fd.write('\n'.join(hist) + '\n')
    except IOError:
        pass

def readHist():
    'Read the history stack from the history file'
    try:
        with open(CDHISTFILE, 'r') as fd:
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

def selectHist(hist, num, tty):
    'Bounds check the entered index and select directory if in range'
    if num < 0 or num >= len(hist):
        tty.write('cdhist: number {} out of range\n'.format(num))
        return 1

    print(hist[num])
    return 0

def searchHist(hist, text, tty):
    'Search back for text in stack and select directory if found'
    for dir in hist[1:]:
        if text in dir:
            print(dir)
            return 0

    tty.write('cdhist: string "{}" not found\n'.format(text))
    return 1

def main():
    'Main code'
    # Main returns a directory name to cd to (as a string). Also returns
    # a status code:
    #
    # 0 = Proceed with real cd command using the single argument provided.
    # 1 = Do not proceed. Just quit.

    # Open the user's tty so we can send him messages
    tty = open('/dev/tty', 'w')

    # Ensure private history file
    os.umask(0o177)

    # Intercept home case immediately
    if len(sys.argv) <= 1:
        print(HOME)
        return 0

    if sys.argv[1][0] == '-':
        # Look for and process cdhist option
        if len(sys.argv) == 2:
            arg = sys.argv[1]

            # This may be a call to just update the directory history. I.e
            # after a successfull shell 'cd'.
            if arg == '-u':
                writeHist(fetchHist())
                return 0

            # List directory stack?
            if arg == '--' or arg == '-l':

                # Fetch the current history
                hist = fetchHist()

                # List the directory stack (in reversed output)
                n = len(hist)
                for dird in reversed(hist):

                    if CDHISTTILDE and dird.startswith(HOME):
                        dird = dird.replace(HOME, '~', 1)

                    n -= 1
                    tty.write('{:3} {}\n'.format(n, dird))

                if arg == '--':
                    # Prompt for index from the screen
                    tty.write('Select directory index [or <enter> to quit]: ')
                    tty.flush()
                    try:
                        line = sys.stdin.readline().strip()
                    except KeyboardInterrupt:
                        return 1

                    if line and line[0] == '/':
                        return searchHist(fetchHist(), line[1:], tty)

                    try:
                        num = int(line, 10)
                    except ValueError:
                        return 1

                    # Select the index given by the user
                    return selectHist(hist, num, tty)

                return 1

            if arg == '-h' or arg == '-?':
                from string import Template
                # Just output help/usage
                tty.write(Template(HELP).substitute(
                    cmd=os.environ.get('CDHISTCOMMAND', 'cd'),
                    size=CDHISTSIZE, tilde=CDHISTTILDE))
                return 1

            if arg == '-':
                # A normal shell can't cd to OLDPWD when it is not set (e.g.
                # just after login). But we may have more history so use it :)
                return selectHist(fetchHist(), 1, tty)

            if len(arg) > 1:
                if arg[1:].isdigit():
                    # Select this directory index
                    return selectHist(fetchHist(), int(arg[1:], 10), tty)

                if arg[:2] == '-/':
                    # Search stack for REGEXP "string" and select that dir
                    return searchHist(fetchHist(), arg[2:], tty)

        if sys.argv[1] == '--':
            del sys.argv[1]
        else:
            tty.write('cdhist: cd command options are not supported\n')
            return 1

    # Fall through to real 'cd' to deal with normal dir
    print(' '.join(sys.argv[1:]))
    return 0

if __name__ == '__main__':
    sys.exit(main())

# vim: se et:
