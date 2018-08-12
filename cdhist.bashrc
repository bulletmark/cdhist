#!/bin/bash
#
# A bash directory stack "cd history" function.
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

# User option: Size of the directory stack
export CDHISTSIZE=${CDHISTSIZE:=31}

# User option: Set the following "TRUE" if you want your home directory
# displayed as a tilde ("~"). Else set FALSE, null, etc.
export CDHISTTILDE=${CDHISTTILDE:=TRUE}

# See help text in accompanying cdhist.py script for usage and more
# information (i.e. type "cd -h" after installation).

# Location of the cdhist.py program.
CDHISTPROG_="/usr/bin/cdhist"

# Redefine user cd command for this session
alias ${CDHISTCOMMAND:-cd}=cd_
function cd_
{
    # Call the worker script to process the argument. The script will
    # return a (possibly different) string argument and a status to
    # indicate whether to proceed with the 'cd' or not.
    _d="$($CDHISTPROG_ "$@")"

    if [ $? -eq 1 ]; then
	return 0
    fi

    # If the 'cd' is successful then call the script again merely so it
    # can record the new working directory in the history stack.
    if 'cd' "$_d"; then
	$CDHISTPROG_ -u
    fi

    return $?
}
