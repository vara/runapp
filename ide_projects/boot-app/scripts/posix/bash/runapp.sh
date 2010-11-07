#!/bin/bash

#
## Author: Grzegorz (vara) Warywoda 
## Since: 14-04-2010 18:50:32
#

#set -x
set -o posix

readonly VERSION=1.0.0
readonly AUTHOR="Grzegorz (vara) Warywoda"
readonly CONTACT="grzegorz.warywoda@verkonwsys.com"

DEBUGCOLOR='\033[32m'
ERRCOLOR='\033[31m'

#
## Run script in testing mode. 
## Don't run external application, just run only script and exit.
#
TESTING_MODE=${TESTING_MODE:-0}

DEBUG=${DEBUG:-0}
CONFIG_FP=${CONFIG_FP:-"runapp.conf"}

PROVIDER="java" #HARD CODE FIXME: after implement maven boot util

SCRIPT_LOCATION=$0
# Step through symlinks to find where the script really is
while [ -L "$SCRIPT_LOCATION" ]; do
  SCRIPT_LOCATION=`readlink -e "$SCRIPT_LOCATION"`
done
SCRIPT_HOME=`dirname "$SCRIPT_LOCATION"`

PATH="$SCRIPT_HOME:$PATH"

##################
##load lib notify
#
#. $SCRIPT_HOME/notify.sh

##################
##load lib timer
#
. $SCRIPT_HOME/timer.sh

t=$(timer)

#
## Print version for this release
#
printVersion(){
  toconsole "v$VERSION"
}

#
# Print info about this script
#
printInfo(){
  toconsole "Author: $AUTHOR\nContact: $CONTACT\nrunapp v$VERSION"
}

#
## Print mesasge saving in first argument.
#

toconsole(){	
	echo -e >&2 $1	
}

#
## Print warning on the console. Function takes one argument who adopt text message
#
warn(){
	toconsole "WARNING: $1"

#Not implemented yet
#	notify $1 

}

#
## Function for debug output. First argument is the text message 
## printed on the console. Second argumnet is the level representing by integer number
## assosiated to this message.
## If the level (second arg.) is less then global variable 'DEBUG' 
## then this message will not appear on console.
#
debug(){

	if [ "$DEBUG" -gt "0" ]; then
		local level=${2:-1}
		if [ "$level" -le "$DEBUG" ]; then
			toconsole "${DEBUGCOLOR}DEBUG${level}:\033[m $1"
		fi
	fi
}

err(){
	toconsole "${ERRCOLOR}ERROR:\033[m $1"
	#notify $1
}

readConfig(){
	for prefix in "" "`pwd`/" "$HOME/"
	do
	  local configName="$prefix$CONFIG_FP"
	  if [ -r "$configName" ];then
		  . $configName
		  break
	  else
		  warn "Config file '$configName' not exist"
	  fi
	done
}

exitScript(){
	
	if [ -n "$WAIT_ON_EXIT" ] ; then
	  
	  if [ "$DEBUG" -gt "1" ]; then
		debug "Wait on exit $WAIT_ON_EXIT" 2
	  fi

		sleep $WAIT_ON_EXIT

	fi

	exit $exitcode
}

#
## Parse config files
## Sequentially input arguments are:
## -path to file containg configuration stuff 
## -type of configuration. Distinguish two of config. types
##		1. with dependency paths. Recommend the use of relative paths by using global variables
##			as well as in shell scripts eg. ${prefix_for_path}/jam_lasica/
##		2. with line by line arguments. Each line is redirected to application in raw format.
##	Function return a string of chars where each line is separeted by space char ' '.
#
parseFile() {
	
	local fileToRead=$1	
	local type=$2
	local currentRow=0
	local line

	if [ -e $fileToRead ];then
		exec<$fileToRead
		
		if [ "$DEBUG" -gt "2" ]; then
		  debug "Prepare parse $fileToRead file. [type:$type]" 3
		fi
		
		while read -e line;	do

			((currentRow++))
			
			if [ "`expr substr "$line" 1 1`" != "$COMMENTCHAR" ];then
			
				line=`eval echo $line`

				if [ "$DEBUG" -gt "3" ]; then
				  debug "[$currentRow]Resolved line: $line" 4
				fi
				
				case "$type" in
					#This section parse and validate path to file stored in '$line'
					"path")
						
						if [ -r "$line" ]; then 
							echo -n "$line:"
						else

							if [ "$DEBUG" -gt "3" ]; then
							  debug "[$currentRow]Can't read from '$line', ignore it !" 4
							fi

						fi
					;;
					"args")
						echo -n " $line"
					;;
					*)
						warn "Parser: Unrecognized input parameter '${type}'"
						return
					;;
				esac
			else

				if [ "$DEBUG" -gt "2" ]; then
				  debug "[$currentRow]Comment-out line:$line" 3
				fi

			fi
		done
		
		if [ "$DEBUG" -gt "2" ]; then
		  debug "Finished" 3
		fi

	else warn "[$fileToRead] File Not found"
	fi
}

resolve_symlink () {
    local file="$1"
    while [ -h "$file" ]; do
        ls=`ls -ld "$file"`
        link=`expr "$ls" : '^.*-> \(.*\)$' 2>/dev/null`
        if expr "$link" : '^/' 2> /dev/null >/dev/null; then
            file="$link"
        else
            file=`dirname "$1"`"/$link"
        fi
    done
    echo "$file"
}

#
## Resolve path to java binary file. If path has not been found 
## then script will exit.
#
checkJava(){

	if [ -z "$JAVA_HOME" ]; then
		#debug "Variable enviroment \$JAVA_HOME not found." 3
		
		if [ -z "$JRE_HOME" ]; then 
			#debug "Variable enviroment \$JRE_HOME not found." 3
			
			if [ -z "$JDK_HOME" ]; then 
				#debug "Variable enviroment \$JDK_HOME not found." 3
			
				case "`uname`" in
					Darwin*)
			#         jdkhome="/System/Library/Frameworks/JavaVM.framework/Versions/1.5/Home"
			#         java_bin=`which java 2>&1`
			#         if [ $? -ne 0 ] || [ -n "`echo \"$java_bin\" | grep \"no java in\"`" ] ; then
			# # no java in path... strange
			#             java_bin=/usr/bin/java
			#         fi
			#         if [ -f "$java_bin" ] ; then
			#             java_version=`"$java_bin" -fullversion 2>&1`
			#             if [ $? -eq 0 ] && [ -n "`echo \"$java_version\" | grep 1.6.0`" ] ; then
			# # don`t use Developer Preview versions
			#                 if [ -z "`echo \"$java_version\" | grep \"1.6.0_b\|1.6.0-b\|1.6.0_01\|1.6.0_04\|-dp\"`" ] ; then
			#                     if [ -f "/System/Library/Frameworks/JavaVM.framework/Versions/1.6/Home/bin/java" ] ; then
			#                         jdkhome="/System/Library/Frameworks/JavaVM.framework/Versions/1.6/Home"
			#                     elif [ -f "/System/Library/Frameworks/JavaVM.framework/Versions/1.6.0/Home/bin/java" ] ; then
			#                         jdkhome="/System/Library/Frameworks/JavaVM.framework/Versions/1.6.0/Home"
			#                     fi
			#                 fi
			#             fi
			#         fi
					;;
					*) 
						local java=`which java`
						if [ -n "$java" ] ; then
							java=`resolve_symlink "$java"`
							
							if [ "$DEBUG" -gt "2" ]; then
							  debug "Resolved symlink for java is '$java'" 3
							fi
							JAVA_BIN=$java
						else
							debug ""
						fi
						
					;;
				esac
				
			else
				#debug "JDK_HOME viarable is set to :"$JDK_HOME 3
				JAVA_BIN="$JDK_HOME/bin/java"
			fi
		else
			#debug "JRE_HOME viarable is set to :"$JRE_HOME 3
			JAVA_BIN="$JRE_HOME/bin/java"
		fi
	else
		#debug "JAVA_HOME viarable is set to :"$JAVA_HOME 3
		JAVA_BIN="$JAVA_HOME/bin/java"
	fi
	
	if [ ! -x "${JAVA_BIN}" ] ; then
		#critical situation
		err "No JAVA found ! Please set variable JAVA_HOME or JRE_HOME path."
		exitcode=2
		exitScript
	fi

	if [ "$DEBUG" -gt "1" ]; then
	  debug "java bin has been resolved properly and was set to "${JAVA_BIN} 2
	fi
}

#
## Check whether the file exists, if not print the warning.
#
checkExistsFile(){
  if [ ! -f "$1" ]; then
	warn "File $1 not exists"
	echo ""
  fi
  echo $1
}

printUsage(){
#TODO:Make better description
  printInfo
  echo -e "\n"
  cat $SCRIPT_HOME/usage.txt
}

#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################

#########################
## Parse input argumnets
#
while test $# -gt 0; do
  symbol="$1"

  if [ "$DEBUG" -gt "1" ]; then
	debug "Parse argument '$symbol'" 2
  fi

  case "$symbol" in
    "--")
    
		shift
		break
    ;;
    -h|--help|-\?)
    
		printUsage
		exit 0
	;;
	-v|--version)
	
		printVersion
		exit 0
	;;
	java|maven)

		PROVIDER=$symbol
		shift
	;;
	--exec|-e)
		EXEC_TOOL=$2
		shift 2
	;;
	--exec=*|-e=*)
		EXEC_TOOL=${1##*=}
		shift
	;;
	--debug|-d)
		DEBUG=$2
		shift 2
	;;
	--debug=*|-d=*)
		DEBUG=${1##*=}
		shift
	;;
	--conf=*|-c=*)
		tmpFilePath=$(checkExistsFile $(eval echo -e "${1##*=}") );  
		if [ ! -z "$tmpFilePath" ]; then  
		  CONFIG_FP=$tmpFilePath
		fi
		shift
	;;
	--conf|-c)
 		tmpFilePath=$(checkExistsFile $(eval echo -e "$2"))
		if [ ! -z "$tmpFilePath" ]; then  
		  CONFIG_FP=$tmpFilePath
		  shift 
		fi
		shift
	;;
	--testingMode|-tm)
		TESTING_MODE=1
		shift
	;;
	--mainClass|-mc)
		if [ ! -z "$2" ]; then
		  MAINCLASS="$2"
		  shift
		fi
		shift
	;;	
	--mainClass=*|-mc=*)
		MAINCLASS=${1##*=}
		shift
	;;
	*)
		if [ -z "$symbol" ]; then
		  break
		fi

		# Try resolve path to project directory
		# NOTE: Only once we allow to define variable PROJECT_DIR.
		#		Any further appeal will be ignoring. 
		#		eg. runapp /path1/ ... /path2/ ...
		#			"/path1/" will be assigned to PROJECT_DIR.
		#		eg. runapp /broken_path_to__dir_or_file ... /path2 ...
		#			"/path2" will be assigned to PROJECT_DIR.
		#		
		if [ ! -n "$absolute_path" ]; then
			#debug "Try resolve path '$symbol'"
			#This method allows to passing path with prefix '~'
			absolute_path=$(eval echo -e "$symbol")
		  
			if [ -d "$absolute_path" ]; then
				PROJECT_DIR=$absolute_path
			else
				warn "'$symbol' is not a directory."
				
				#@Author Grzegorz (vara) Warywoda 2010-08-24 23:41:03 CEST
				#Commented-out for fix passing application argumnets witchout script argumnets
				#printUsage
				#exit 1
				unset absolute_path #clear variable if is not a path
				shift
			fi
		else
			warn "Detected attempt to overide variable PROJECT_DIR by '$symbol'. Operation not permited."
			break
		fi

		shift
		
	esac  
done

USER_ARGS_TO_APP="$USER_ARGS_TO_APP $*"

########################################

PROJECT_DIR=${PROJECT_DIR:-`pwd`}

if [ -d "$PROJECT_DIR" ]; then PROJECT_DIR=`readlink -e "$PROJECT_DIR"` > /dev/null 2>&1
	
	if [ "$PROJECT_DIR" != `pwd` ]; then
	  cd $PROJECT_DIR
	fi
else
	warn "Variable PROJECT_DIR '$PROJECT_DIR' is not path to directory. Configuration files will be ignore."	
fi

########################################

M2_REPOSITORY=${M2_REPOSITORY:-"$HOME/.m2/repository"}
COMMENTCHAR=${COMMENTCHAR:-"#"}
WAIT_ON_EXIT=${WAIT_ON_EXIT:-0}

if [ "$DEBUG" -gt "1" ]; then
  debug "Config file path = $CONFIG_FP" 2
fi

readConfig

if [ "$TESTING_MODE" -gt "0" ]; then  warn "Script running in testing mode !"
  #if [ "$WAIT_ON_EXIT" -le "0" ]; then WAIT_ON_EXIT=2; fi
fi

echo $DEBUG | grep "[^0-9]" > /dev/null 2>&1	
if [ "$?" -eq "0" ]; then	
	warn "Sorry, 'DEBUG=$DEBUG' - variable must be positive number. Try 'export DEBUG=1'. For this instance 'DEBUG' will be set to 0."
	DEBUG=0
fi

if [ "$DEBUG" -gt "0" ]; then
  debug "PROJECT_DIR=$PROJECT_DIR" 1
fi

checkJava

DEPENDENCY_FP=${DEPENDENCY_FP:-"$PROJECT_DIR/runapp.dep"}
JVM_ARGS_FP=${JVM_ARGS_FP:-"$PROJECT_DIR/runapp.jvmargs"}


if [ -z "$MAINCLASS" ]; then
  err "Main class not found. Please set 'MAINCLASS' variable."
  exit 3
fi

CLASSPATH=$(parseFile $DEPENDENCY_FP "path")

if [ "$DEBUG" -gt "2" ]; then
  debug "CLASSPATH:$CLASSPATH" 3
fi

JVM_ARGS=$(parseFile $JVM_ARGS_FP "args")

case "$PROVIDER" in
    java)
		
		EXECPATH="$JAVA_BIN"	
		EXECARGS=$JVM_ARGS
		
		if [ -n "$CLASSPATH" ];then 
			EXECARGS="$EXECARGS -cp $CLASSPATH"
		fi
		EXECARGS="$EXECARGS $MAINCLASS $USER_ARGS_TO_APP"
    ;;
    maven)
    	
    	export MAVEN_OPTS=$JVM_ARGS
    	EXECPATH="mvn"
    	EXECARGS="-e --no-plugin-updates --batch-mode -Dexec.args=$* exec:java -Dexec.mainClass=$MAINCLASS"
		#mvn -e --no-plugin-updates --batch-mode -cp .:$CLASSPATH -Dexec.args=$@ exec:java -Dexec.mainClass=$MAINCLASS
    ;;
    *)
		warn "Unrecongnized provider '$PROVIDER'."
		printUsage
		exit 0
esac

if [ "$DEBUG" -gt "0" ]; then

  debug "`$JAVA_BIN -version 2>&1`"
  debug "Exec tool: $EXEC_TOOL"
  debug "Execution Bin: $EXECPATH"
  debug "JVM Parameters: $JVM_ARGS"
  debug "Main class: $MAINCLASS"
  debug "User args: $USER_ARGS_TO_APP"
fi

  toconsole "Elapsed time of boot application : $(timer $t)"

if [ "$TESTING_MODE" -le "0" ]; then

	#Too huge string
	#debug "Execution Parameters: $EXECARGS"

workTime=$(timer)

	eval $EXEC_TOOL $EXECPATH $EXECARGS '&'
	PID=$!
	
	if [ "$DEBUG" -gt "0" ]; then
	  debug "Created new process with PID:$PID."
	fi

	#
	## Set hook (intercept) for EXIT interrupt (from shell sent directly by ctrl+x).
	#
	trap "kill $PID" EXIT

	#
	## Wait for Punisher
	#
	wait $PID
	exitcode=$?
	
	if [ "$DEBUG" -gt "0" ]; then
	  debug "Application working time: $(timer $workTime)"
	fi

	#
	## If the application has been closed normaly (without any external influence)
	## then we dont have what do kill ... clear action asigned to EXIT interrupt.
	#
	trap '' EXIT
	
	if [ "$DEBUG" -gt "0" ]; then
	  debug "The application has finished work ! [exitcode:$exitcode]"
	fi
fi
exitScript
