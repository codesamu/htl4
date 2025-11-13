// access OS ressources from C
//  w.mueller@tsn.at 2020/02/03

// compile with 
//     gcc -o AAB03-OSfromC AAB03-OSfromC.c -lm -lpthread

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include <time.h>
#include <pthread.h>

const size_t M=1024*1024;

int cpu_loop_cnt=100;

void burn_cpu(int ntimes) {
    int j;    double x=2;
    printf("... cpu loop %d Mio times x=sin(x)\n",ntimes);
    for( j=0; j<ntimes; j++) {
         int i;
         for (i=0;i<M ; i++) x=sin(x);
    };
}

void my_thread(void *ptr) {
   burn_cpu(cpu_loop_cnt);
}

void menu() {
    printf("\ncommands:\n");
    printf(" c 500      reserve 500 1M blocks with calloc\n");
    printf(" f          free last reserved buffer\n");
    printf(" w 1000     write 1000 times at random pos to buffer\n");
    printf(" l 10       loop cpu with 10 times 1 mio x=sin(x)\n");
    printf(" t 5        loop cpu with 5 threads, each %d times 1 mio x=sin(x)\n", cpu_loop_cnt);
    printf(" e          end program\n");
    printf("enter command:");
}

void thread_test(int n) {
    pthread_t thp[100] ;
    if (n>99) n=99;
    int i;
    for(i=0;i<n ; i++) {  // Threats anlegen und starten
        if ( pthread_create ( &thp[i] , NULL, (void*) &my_thread , NULL) ) perror ( "could not create thread" );
    }
    for(i=0;i<n ; i++) {
        pthread_join ( thp[i] , NULL) ;  // Warten bis threats fertig sind
    }
}

int main()
{
    size_t n, bsize=0,pos;
    while(1)
    {
        menu();
        char command;
        char zeile[100];
        fgets(zeile,99,stdin);
        sscanf(zeile,"%c %ld", &command , &n);
        char *buffer, *l;
        int j;
        switch ( command)
        {  case 'c' :
             buffer=calloc(n, M);
             bsize=n;
             printf("%5ld 1M Bloecke reserviert ab Adresse: %p\n",n,buffer);
             printf("                           bis Adresse: %p\n",buffer+n*M);
            break;
           case 'w':
           case 'W':
            printf("fill %ld times a random position with 1MByte of 0xff\n",n);
             for( j=0; j<n; j++) {
              pos= M*(rand()%bsize);
              l=buffer+pos;
              if( command == 'W' ) printf("write at offset %10ld %p \n",pos,l);
              int i;
              for (i=0;i<M ; i++) *(l++)=0xff;
             };
             break;
           case 'f':
             free(buffer);
             break;
           case 'l':
             printf("cpu loop %ld Mio times x=sin(x)\n",n);
             burn_cpu(n);
             cpu_loop_cnt=n;
             break;
           case 't':
             printf("cpu loop with %ld threads %d Mio times x=sin(x)\n",n,cpu_loop_cnt);
             thread_test(n);
             break;
           case 'e':
                 return(0);
        }
    }
    return 0;
}

