#!/bin/sh
#
# Dowloaded from:http://www.linuxjournal.com/content/use-date-command-measure-elapsed-time
#
# Elapsed time.  Usage:
#
#   t=$(timer)
#   ... # do something
#   printf 'Elapsed time: %s\n' $(timer $t)
#      ===> Elapsed time: 0:01:12
#
#
#####################################################################
# If called with no arguments a new timer is returned.
# If called with arguments the first is used as a timer
# value and the elapsed time is returned in the form HH:MM:SS.
#

#set -x
PATH=".:$PATH"

timer() {
  timerC $*
}

#
## Using 'date' command for get current time value
#
timerD()
{
    if [ $# -eq 0 ]; then
        getMillisec
    else
		local etime=$(getMillisec)
		local stime=$1        

        if [ -z "$stime" ]; then stime=$etime; fi

        dt=$((etime - stime))
        printf '%dms' $dt
    fi
}

getMillisec() {

	local millisec=$((`date +10#%s` * 1000))	
	local nanosec=$((`date +10#%N`))
#		echo "n:$nanosec">&2
	millisec=$((millisec + $nanosec /1000000))
	echo $millisec
}

#
## Using c implementation for get current time value
## (gettimeofday function)
#
timerC() {
	if [ $# -eq 0 ]; then
	  time_m
	else
	  dt=`time_m $1`
	  printf '%dms' $dt
	fi
}

#echo $(timerC)
