#!/bin/bash
# Installation script.
# (C) Mark Blakeney, markb@berlios.de, May 2012.

PROG="cdhist.py"
BFIL="bashrc_cdhist"

if [ "$(id -un)" = "root" ]; then
    BINDIR="/usr/local/bin"
    ETCFIL="/usr/local/etc/$BFIL"
    BINEDT=0
else
    LITDIR='$HOME/bin'
    BINDIR=$(eval echo $LITDIR)
    ETCFIL="$HOME/.$BFIL"
    BINEDT=1
fi

usage() {
    echo "Usage: $(basename $0) [-options]"
    echo "Options:"
    echo "-r <remove/uninstall>"
    echo "-l <list only>"
    exit 1
}

REMOVE=0
LIST=0
while getopts rl c; do
    case $c in
    r) REMOVE=1;;
    l) LIST=1;;
    ?) usage;;
    esac
done

shift $((OPTIND - 1))

if [ $# -ne 0 ]; then
    usage
fi

# Delete or list file/dir
clean() {
    local tgt=$1

    if [ -e $tgt -o -h $tgt ]; then
	if [ -d $tgt ]; then
	    if [ $REMOVE -eq 1 ]; then
		echo "Removing $tgt/"
		rm -rf $tgt
		return 0
	    else
		ls -ld $tgt/
	    fi
	elif [ $REMOVE -ne 0 ]; then
	    echo "Removing $tgt"
	    rm -r $tgt
	    return 0
	else
	    ls -l $tgt
	fi
    fi

    return 1
}

ETCDIR=$(dirname $ETCFIL)

if [ $REMOVE -eq 0 -a $LIST -eq 0 ]; then
    mkdir -p $BINDIR
    install -CDv $PROG -t $BINDIR

    t=$(mktemp)
    if [ $BINEDT -ne 0 ]; then
	cp $BFIL $t
	sed -i 's#^\(CDHISTPROG_=\).*$#\1"'"$LITDIR/$PROG\""# $t
	BFIL=$t
    fi

    mkdir -p $ETCDIR
    install -CDv -m 644 $BFIL -T $ETCFIL
    rm -f $t
else
    if clean $BINDIR/$PROG; then
	rmdir --ignore-fail-on-non-empty $BINDIR
    fi
    if clean $ETCFIL; then
	rmdir --ignore-fail-on-non-empty $ETCDIR &>/dev/null
    fi
fi

exit 0
