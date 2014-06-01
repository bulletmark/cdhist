#!/usr/bin/env python
#
# A bash directory stack "cd history" function.
#
# Copyright (C) 2010 Mark Blakeney, markb@berlios.de. This program is
# distributed under the terms of the GNU General Public License.
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
# See help text below and the accompanying bashrc_cdhist and README.

'''A directory stack "cd history" function'''

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
A simple "cd history" function which intercepts your shell "cd"
command to maintain a stack of directories visited.

Usage examples:
cd somepath   : Add "somepath" to your directory stack and cd there.
cd -l         : List the current stack and its indices.
cd -n         : cd to stack index "n".
cd -/string   : Search back through stack for REGEXP "string" and cd there.
cd --         : List the stack and its indices then prompt for dir to select.
cd -h|?       : Print this help.
All other arguments are passed on to the normal cd command.
Environment   : You have CDHISTSIZE=%d, CDHISTTILDE=%s
''' % (CDHISTSIZE, CDHISTTILDE)

# Constants and definitions
HOME = os.path.expanduser('~')
CDHISTFILE = os.path.join(HOME, '.cd_history')

def writeHist(hist):
    '''Write the passed history stack to the history file'''
    try:
        with open(CDHISTFILE, 'w') as fd:
            fd.write('\n'.join(hist) + '\n')
    except IOError:
        pass

def readHist():
    '''Read the history stack from the history file'''
    try:
        with open(CDHISTFILE, 'r') as fd:
            hist = [d.rstrip('\n') for d in fd]
    except IOError:
        # No file, assume empty history
        hist = []

    return hist

def fetchHist():
    '''Update and return the current history stack'''

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
    '''Bounds check the entered index and select directory if in range'''
    if num < 0 or num >= len(hist):
        tty.write('cd history number %d out of range\n' % num)
        sys.exit(1)

    return hist[num]

def searchHist(hist, text, tty):
    '''Search back for text in stack and select directory if found'''
    for dir in hist[1:]:
        if text in dir:
            return dir

    tty.write('String "%s" not found\n' % text)
    sys.exit(1)

def main():
    '''Main code'''

    # Main returns a directory name to cd to (as a string). Also returns
    # a status code:
    #
    # 0 = Proceed with real cd command using the single argument provided.
    # 1 = Do not proceed. Just quit.
    # 2 = Proceed using the multiple arguments provided.

    # Open the user's tty so we can send him messages
    tty = open('/dev/tty', 'w')

    # Ensure private history file
    os.umask(0o177)

    # Check arguments
    if len(sys.argv) <= 1:
        tty.write('This program should be called from bashrc_cdhist\n')
        sys.exit(1)

    # This may be a call to just update the directory history. I.e
    # after a successfull shell 'cd'.
    if sys.argv[1] == '-u':
        writeHist(fetchHist())
        sys.exit(0)

    # Process the arguments
    if sys.argv[1] != '--':
        tty.write('Odd argument ' + sys.argv[1] + ' ?\n')
        sys.exit(1)

    if len(sys.argv) <= 2:
        arg = HOME
    elif len(sys.argv) == 3:
        arg = sys.argv[2]
    else:
        # Not sure what is being given here but let cd deal with it
        print(' '.join(sys.argv[2:]))
        sys.exit(2)

    # List directory stack?
    if arg == '--' or arg == '-l':

        # Fetch the current history
        hist = fetchHist()

        # List the directory stack (in reversed output)
        n = len(hist)
        for dir in hist[::-1]:

            if CDHISTTILDE and dir.startswith(HOME):
                dir = dir.replace(HOME, '~', 1)

            n -= 1
            tty.write('%3d %s\n' % (n, dir))

        if arg == '--':
            # Prompt for index from the screen
            tty.write('Select directory index [or <enter> to quit]: ')
            tty.flush()
            try:
                num = sys.stdin.readline().strip()
            except KeyboardInterrupt:
                sys.exit(0)

            if num and num.isdigit():
                # Select the index given by the user
                print(selectHist(hist, int(num, 10), tty))
                sys.exit(0)

        sys.exit(1)
    elif arg == '-h' or arg == '-?':
        # Just output help/usage
        tty.write(HELP)
        sys.exit(1)
    elif arg == '-':
        # A normal shell can't cd to OLDPWD when it is not set (e.g.
        # just after login). But we may have more history so use it :)
        print(selectHist(fetchHist(), 1, tty))
    elif arg[0] == '-' and arg[1:].isdigit():
        # Select this directory index
        print(selectHist(fetchHist(), int(arg[1:], 10), tty))
    elif arg[:2] == '-/':
        # Search stack for REGEXP "string" and select that dir
        print(searchHist(fetchHist(), arg[2:], tty))
    else:
        # Fall through to real 'cd' to deal with normal dir
        print(arg)

    sys.exit(0)

if __name__ == '__main__':
    main()

# vim: se et:
