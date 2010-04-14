#!/bin/sh

#Author Grzegorz (vara) Warywoda 
#Since 14-04-2010 18:55:43

#set -x
set -o posix

if test $# -eq 0 ; then
	echo usage: "${0##/*} [Dir name]"
	exit
fi

for filename in `grep -rl "$2" $1` ; do
	if test -e $filename ; then		
		echo  "$filename"
		echo `fgrep $filename -bHe "$2"`
	else
		echo "Cannot find $filename"
	fi
done
