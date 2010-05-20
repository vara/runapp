#!/bin/sh

#Author Grzegorz (vara) Warywoda 
#Since 14-04-2010 18:50:32

#set -x
set -o posix

DEBUGCOLOR='\033[32m'
ERRCOLOR='\033[31m'

toconsole(){	
	echo -e >&2 $1	
}

warn(){
	toconsole "WARNING: $1"
}

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
		debug "Config file '$configName' not exist"  2
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

		debug "Prepare parse $fileToRead file. [type:$type]" 
		
		while read -e line;	do

			((currentRow++))
			
			if [ "`expr substr "$line" 1 1`" != "$COMMENTCHAR" ];then
			
				case "$type" in
					#This section parse and validate path to file stored in '$line'
					"path")

						line=`eval echo $line`
						debug "Found path: $line" 3
						
						if [ -r "$line" ]; then 
							echo -n "$line:"
						else 
							debug "[$currentRow]Can't read from '$line', ignore it !" 2
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
				debug "[$currentRow]Commented line:$line" 2
			fi
		done

		debug "Finished" 2

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

#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################

DEBUG=${DEBUG:-0}

SCRIPT_LOCATION=$0
# Step through symlinks to find where the script really is
while [ -L "$SCRIPT_LOCATION" ]; do
  SCRIPT_LOCATION=`readlink -e "$SCRIPT_LOCATION"`
done

SCRIPT_HOME=`dirname "$SCRIPT_LOCATION"`

PROJECT_DIR=${PROJECT_DIR:-`pwd`}

if [ -d "$PROJECT_DIR" ]; then

	PROJECT_DIR=`readlink -e "$PROJECT_DIR"` > /dev/null 2>&1
	cd $PROJECT_DIR
else
	warn "Variable PROJECT_DIR '$PROJECT_DIR' is not path to directory. Configuration files will be ignored."	
fi

M2_REPOSITORY=${M2_REPOSITORY:-"$HOME/.m2/repository"}
COMMENTCHAR=${COMMENTCHAR:-"#"}
WAIT_ON_EXIT=${WAIT_ON_EXIT:-0}

readConfig

debug "PROJECT_DIR=$PROJECT_DIR" 3

echo $DEBUG | grep "[^0-9]" > /dev/null 2>&1	
if [ "$?" -eq "0" ]; then	
	warn "Sorry, 'DEBUG=$DEBUG' - variable must be positive number. Try 'export DEBUG=1'. For this instance 'DEBUG' will be set to 0."
	DEBUG=0
fi

checkJava

DEPENDENCY_FILE=${DEPENDENCY_FILE:-"$PROJECT_DIR/runapp.dep"}
JVM_ARGS_FILE=${JVM_ARGS_FILE:-"$PROJECT_DIR/runapp.jvmargs"}

if [ -z "$MAINCLASS" ]; then
  err "Main class not found. Please set 'MAINCLASS' variable."
  exit 3
fi

CLASSPATH=$(parseFile $DEPENDENCY_FILE "path")
debug "CLASSPATH:$CLASSPATH" 3

JVM_ARGS=$(parseFile $JVM_ARGS_FILE "args")
debug "JVMARGS:$JVM_ARGS" 3

case "$1" in
    java)
		shift
		EXECPATH="$JAVA_BIN"	
		EXECARGS=$JVM_ARGS
		
		if [ -n "$CLASSPATH" ];then 
			EXECARGS="$EXECARGS -cp $CLASSPATH"
		fi
		EXECARGS="$EXECARGS $MAINCLASS $*"
    ;;
    maven)
    	shift
    	export MAVEN_OPTS=$JVM_ARGS
    	EXECPATH="mvn"
    	EXECARGS="-e --no-plugin-updates --batch-mode -Dexec.args=$* exec:java -Dexec.mainClass=$MAINCLASS"
		#mvn -e --no-plugin-updates --batch-mode -cp .:$CLASSPATH -Dexec.args=$@ exec:java -Dexec.mainClass=$MAINCLASS
    ;;
    *)
		echo "Usage: $0 [java,maven] [parameters to pass to the application]"
		exit 1
esac

debug "Execution Path: $EXECPATH"
debug "Execution Parameters: $EXECARGS"
debug "Main class: $MAINCLASS"

eval $EXECPATH $EXECARGS '&'
PID=$!
debug "Created new process with PID:$PID."

trap "kill $PID" EXIT
wait $PID
exitcode=$?
trap '' EXIT
debug "Application completed work ! [exitcode:$exitcode]"
exitScript
