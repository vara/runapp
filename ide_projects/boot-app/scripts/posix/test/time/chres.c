#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <time.h>

int clock_getres (clockid_t clockid, struct timespec* res)
{
        return syscall(SYS_clock_getres, clockid, res);
}

int main()
{
        struct timespec tp;

        int retVal = clock_getres(CLOCK_MONOTONIC,&tp);

        printf("clock_getres returned %d resolution is %d seconds and %d nanoseconds\n", retVal,tp.tv_sec, tp.tv_nsec);

        return 0;
}