#!/bin/bash
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

function timer()
{
    if [[ $# -eq 0 ]]; then
        getMilisec
    else
        local stime=$1
        local etime=$(getMilisec)

        if [[ -z "$stime" ]]; then stime=$etime; fi

        dt=$((etime - stime))
        #ds=$((dt % 60))
        #dm=$(((dt / 60) % 60))
        #dh=$((dt / 3600))
        printf '%dms' $dt
    fi
}

function getMilisec(){

	local millisec=$((`date +%s` * 1000))	
	local nanosec=`date +%N`
#		echo "n:$nanosec">&2
	millisec=$((millisec + ${nanosec#0} /1000000))
	echo $millisec
}
