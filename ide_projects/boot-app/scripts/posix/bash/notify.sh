#!/bin/sh

NOTIFY_EXE="/usr/bin/notify-send"
INITIALIZED=0

sendToNotify(){

  local textMessage

  for symbol  in  $@ ; do
	case "$symbol" in
	  *)
		textMessage="$textMessage $symbol"
	  ;;
	esac
  done

  $NOTIFY_EXE "$(date +'%H:%M:%S')" "$textMessage" 
}

#
## Send notify to system gui.
#

function notify(){

	if [ $INITIALIZED = 0 ]; then

	  if [ -e "$NOTIFY_EXE" ]; then
		  ((INITIALIZED++))
	  else
		  ((INITIALIZED--))
		  echo >&2 -e "WARNING: $NOTIFY_EXE -- not found. Pleas install libnotify-bin"
	  fi

	fi

	if [ $INITIALIZED = 1 ]; then
	  sendToNotify $@
	fi
}

