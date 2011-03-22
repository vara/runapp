#!/bin/sh

#Author Grzegorz (vara) Warywoda 
#Since 14-04-2010 18:55:43

#set -x
set -o posix

if test $# -eq 0 ; then
	echo usage: "${0##/*} [Dir name]"
	exit
fi

/usr/bin/find $0 -type f -name $1 -print0 | xargs -0 /usr/bin/grep --color=auto -n -C 3 -w "$2"