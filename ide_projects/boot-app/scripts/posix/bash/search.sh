#!/bin/sh

#Author Grzegorz (vara) Warywoda 
#Since 14-04-2010 18:55:43

#set -x
set -o posix

if test $# -eq 0 ; then
	echo usage: "${0##/*} [Dir name]"
	exit
fi

outs(){
	echo -e "\t${currentRow})${2}"	
}

for filename in `grep -rl "$2" $1` ; do
	if test -e $filename ; then		
		echo  "------ Start parsing $filename ------"
#str="`fgrep $filename -bHe "$2"`\n"
		exec<$filename
		currentRow=0;
		while read -e line;	do
			let currentRow++
			line=`echo $line | grep -bHe "$2"`
			
			if [ -n "$line" ]; then
				outs $line
			fi
		done
		echo  "------ Finished parsing $filename ------"
	else
		echo "Cannot find $filename"
	fi
done
