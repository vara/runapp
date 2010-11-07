/**
 *	Author: Grzegorz (vara) Warywoda
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

typedef unsigned long tmval;

static struct timeval time;

inline tmval getTimeOfMilli();

inline tmval diffTime(tmval,tmval);


/**
 *	Application can be start up with one parameter.
 *	Where the param should be integer number ( exacly time in milliseconds ).
 *	Returned value will be the difference between current time and value parameter.
 *	IF application will be start up witchout any parameter then result will be the current time in milliseconds.
 * 	In both cases calculated results will be passed to stdout.
 *
 * Usage:
 * 		time <param | no param>
 *
 */
int main(int argc , char * argv[]){

    //current time
    tmval ctime = getTimeOfMilli();

    if(argc == 1){
        printf("%ld",ctime);

    }else if (argc >= 2){
        if(argc > 2 ){
            fprintf(stderr,"Unrecognized number of input parameters [%d]. Expected 1\n",argc);
        }
        //start time
        tmval stime = strtoul(argv[1],NULL,0);

        printf("%ld", diffTime(stime,ctime) );

    }

    return 0;
}

inline tmval diffTime(tmval start,tmval stop){
    return stop - start;
}

inline tmval getTimeOfMilli(){
  
  gettimeofday(&time, 0);

  return (tmval) ( (time.tv_sec * 1000l) + (time.tv_usec / 1000l) );
}