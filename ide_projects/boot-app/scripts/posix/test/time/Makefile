#Makefile

MKDIR=mkdir
CP=cp
GREP=grep
NM=nm
CCADMIN=CCadmin
RANLIB=ranlib
CC=gcc
CCC=g++
CXX=g++
FC=gfortran
AS=as
LDCONF=/sbin/ldconfig
LN=ln

CFLAGS = -Wall -g -c -O2

OBJS=time.o time

build :  $(OBJS)
	chmod +x $(OBJS)
	
time.o:
	# Compile $@ file 
	$(CC) $(CFLAGS)  time.c -o $@

chres:
	$(CC) $(CFLAGS)  chres.c 
	chmod +x $@

clean: $(OBJS)
	#Clean-up
	rm $(OBJS)
	