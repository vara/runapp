#!/bin/sh

#
#Author Grzegorz (vara) Warywoda 
#Since 14-04-2010 18:50:32
#

#set -x
set -o posix

readonly VERSION=1.0.0
readonly AUTHOR="Grzegorz Warywoda"

DEBUGCOLOR='\033[32m'
ERRCOLOR='\033[31m'

#
##Print version for this release
#
printVersion(){
  toconsole "$AUTHOR \nrunapp ver. $VERSION"
}

#
##Print mesasge saving in first argument.
#

toconsole(){	
	echo -e >&2 $1	
}

#
## Print warning on the console. Function takes one argument who adopt text message
#
warn(){
	toconsole "WARNING: $1"
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
}

readConfig(){
	local configName="`pwd`/runapp.conf"
	if [ -r $configName ];then
		. $configName
	else
		warn "Config file '$configName' not exist"
	fi
}

exitScript(){
	
	if [ -n "$WAIT_ON_EXIT" ] ; then
		debug "Wait on exit $WAIT_ON_EXIT"
		sleep $WAIT_ON_EXIT
	fi

	exit $exitcode
}

parseFile() {
	
	local fileToRead=$1	
	local type=$2
	local currentRow=0
	local line

	if [ -e $fileToRead ];then
		exec<$fileToRead

		debug "Prepare parse $fileToRead file. [type:$type]" 3
		
		while read -e line;	do

			((currentRow++))
			
			if [ "`expr substr "$line" 1 1`" != "$COMMENTCHAR" ];then
			
				line=`eval echo $line`
				debug "[$currentRow]Resolved line: $line" 4
				
				case "$type" in
					#This section parse and validate path to file stored in '$line'
					"path")
						
						if [ -r "$line" ]; then 
							echo -n "$line:"
						else 
							debug "[$currentRow]Can't read from '$line', ignore it !" 4
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
				debug "[$currentRow]Commented line:$line" 3
			fi
		done

		debug "Finished" 3

	else warn "[$fileToRead] File Not found"
	fi
}

#
## Function resolve path from '~/' to '/home/$USER_NAME/'
#

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
# Resolve path to java binary file. If path has not been found 
# then script will exit.
#

checkJava(){

	if [ -z "$JAVA_HOME" ]; then
		debug "Variable enviroment \$JAVA_HOME not found." 3
		
		if [ -z "$JRE_HOME" ]; then 
			debug "Variable enviroment \$JRE_HOME not found." 3
			
			if [ -z "$JDK_HOME" ]; then 
				debug "Variable enviroment \$JDK_HOME not found." 3
			
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
							debug "Resolved symlink for java '$java'" 3
							JAVA_BIN=$java
						else
							debug ""
						fi
						
					;;
				esac
				
			else
				debug "JDK_HOME viarable is set to :"$JDK_HOME 3
				JAVA_BIN="$JDK_HOME/bin/java"
			fi
		else
			debug "JRE_HOME viarable is set to :"$JRE_HOME 3
			JAVA_BIN="$JRE_HOME/bin/java"
		fi
	else
		debug "JAVA_HOME viarable is set to :"$JAVA_HOME 3
		JAVA_BIN="$JAVA_HOME/bin/java"
	fi
	
	if [ ! -x "${JAVA_BIN}" ] ; then
		#critical situation
		err "No JAVA found ! Please set variable JAVA_HOME or JRE_HOME path."
		exitcode=2
		exitScript
	fi
	
	debug "java bin has been resolved properly and was set to "${JAVA_BIN} 2

}

#
#check whether the file exists, if not print the warning.
#
checkExistsFile(){
  if [ ! -f "$1" ]; then
	warn "File $1 not exists"
  fi
}

printUsage(){
  echo -e "Usage:\n\t $0 [root-directory (optional) ] [java|maven] -- [parameters to pass to the application]"
}


#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################

DEBUG=${DEBUG:-0}

STARTER="java" #HARD CODE FIXME: after implement maven boot util

SCRIPT_LOCATION=$0
# Step through symlinks to find where the script really is
while [ -L "$SCRIPT_LOCATION" ]; do
  SCRIPT_LOCATION=`readlink -e "$SCRIPT_LOCATION"`
done
SCRIPT_HOME=`dirname "$SCRIPT_LOCATION"`

########################################
#Parse input argumnets
for symbol  in  $@ ; do
  
  debug "Parse argument '$symbol'" 2
  case "$symbol" in
    --)
		shift
		break
    ;;
    -h|--help)
		printUsage
		exit 0
	;;
	-v|--version)
		printVersion
		exit 0
	;;
	java|maven)

		STARTER=$symbol
		shift
	;;
	--debug|-d)
		shift
		DEBUG=$1
		shift
	;;
	--debug=*|-d=*)
		warn "Combine parameter not supported yet !"
		shift
	;;
	*)
		# Try resolve path to project directory
		if [ ! -n "$absolute_path" ]; then
			debug "Try resolve path '$1'"
			absolute_path=$(eval echo -e "$1")
		  
			if [ -d "$absolute_path" ]; then
				PROJECT_DIR=$absolute_path
			else
				warn "'$1' is not a directory."
				absolute_path="" #clear variable if is not a path
			fi
		else
			warn "Detected attempt to overide variable PROJECT_DIR by '$1'. Operation not permited."
		fi
		
		shift
	esac  
done

USER_ARGS_TO_APP="$*"

########################################

PROJECT_DIR=${PROJECT_DIR:-`pwd`}

if [ -d "$PROJECT_DIR" ]; then

	PROJECT_DIR=`readlink -e "$PROJECT_DIR"` > /dev/null 2>&1
	
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

readConfig

echo $DEBUG | grep "[^0-9]" > /dev/null 2>&1	
if [ "$?" -eq "0" ]; then	
	warn "Sorry, 'DEBUG=$DEBUG' - variable must be positive number. Try 'export DEBUG=1'. For this instance 'DEBUG' will be set to 0."
	DEBUG=0
fi

debug "PROJECT_DIR=$PROJECT_DIR" 3

checkJava

DEPENDENCY_FILE=${DEPENDENCY_FILE:-"$PROJECT_DIR/runapp.dep"}
JVM_ARGS_FILE=${JVM_ARGS_FILE:-"$PROJECT_DIR/runapp.jvmargs"}

(checkExistsFile $DEPENDENCY_FILE)
(checkExistsFile $JVM_ARGS_FILE)

if [ -z "$MAINCLASS" ]; then
  err "Main class not found. Please set 'MAINCLASS' variable."
  exit 3
fi

CLASSPATH=$(parseFile $DEPENDENCY_FILE "path")
debug "CLASSPATH:$CLASSPATH" 3

JVM_ARGS=$(parseFile $JVM_ARGS_FILE "args")

case "$STARTER" in
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
		warn "Unrecongnized starter '$STARTER'."
		printUsage
		exit 0
esac

debug "Execution Path: $EXECPATH"
debug "JVM Parameters: $JVM_ARGS"
debug "Main class: $MAINCLASS"
debug "User args: $USER_ARGS_TO_APP"

#Too huge string
#debug "Execution Parameters: $EXECARGS"

eval $EXECPATH $EXECARGS '&'
PID=$!
debug "Created new process with PID:$PID."

trap "kill $PID" EXIT
wait $PID
exitcode=$?
trap '' EXIT
debug "Application completed work ! [exitcode:$exitcode]"
exitScript