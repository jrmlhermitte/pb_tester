#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>



typedef struct write_args{
    int numlines;
    char* filename;
} write_args;

void test_write(write_args *wargs);

int main(int argc, char* argv[]){
    if(argc != 4){
        printf("Error, received %d arguments.\n",argc);
        printf("Expected 3\n");
        printf("Usage: pb_test_write prefix(string) numlines(int) num(int)\n");
        return 0;
    }
    char *prefix;
    prefix=argv[1];

    int numlines;
    numlines = atoi(argv[2]);

    int n;
    n = atoi(argv[3]);
    pthread_t tids[n];

    char *filenames[n];
    char *str;
    write_args wargs_arr[n];

    int i;
    for(i=0; i<n; i++){
        str = (char *)malloc(21 * sizeof(char));
        sprintf(str, "%s%05d.txt", prefix, i);
        filenames[i] = str;
    }
    // for each of these we want threads
    for(i=0; i<n; i++){
        //test_write(filenames[i]);
        wargs_arr[i].numlines=numlines;
        wargs_arr[i].filename=filenames[i];
        pthread_create((pthread_t *)(tids+i), NULL, (void *)&test_write, (void *)(&wargs_arr[i]));
    }
    // wait for threads to finish
    for(i=0; i<n; i++){
        pthread_join(*(pthread_t *)(tids+i), NULL);
    }
    return 1;
}

void test_write(write_args *wargs){
    FILE *f;
    int timestamp, timestamp_ns, index, value;
    int i;

    timestamp=0;timestamp_ns=0;index=0;value=0;

    printf("Writing to %s\n", wargs->filename);
    printf("Writing %d lines total\n", wargs->numlines);
    f = fopen(wargs->filename, "w");
    for(i=0; i < wargs->numlines; i++){
        fprintf(f, "%010d\t%09d\t%09d\t%#010x\n", timestamp, timestamp_ns, index, value);
        timestamp++;timestamp_ns++;index++;value++;
    }
    fclose(f);
}
