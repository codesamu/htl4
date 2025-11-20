// os_from_c_tcp.c - access OS resources from C with TCP connect
// w.mueller@tsn.at 2020/02/03 + TCP extension 2025/11/20
// compile with 
//     gcc -o AAB03-OSfromC AAB03-OSfromC.c -lm -lpthread

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

const size_t M=1024*1024;
int cpu_loop_cnt=100;

// ========================= CPU burn ==========================
void burn_cpu(int ntimes) {
    int j;    
    double x=2;
    printf("... cpu loop %d Mio times x=sin(x)\n",ntimes);
    for( j=0; j<ntimes; j++) {
         int i;
         for (i=0;i<M ; i++) x=sin(x);
    }
}

void my_thread(void *ptr) {
   burn_cpu(cpu_loop_cnt);
}

void thread_test(int n) {
    pthread_t thp[100] ;
    if (n>99) n=99;
    int i;
    for(i=0;i<n ; i++) {
        if ( pthread_create ( &thp[i] , NULL, (void*) &my_thread , NULL) )
            perror("could not create thread");
    }
    for(i=0;i<n ; i++) {
        pthread_join ( thp[i] , NULL) ;
    }
}

// ========================= TCP connect ==========================
int tcp_connect(const char *host, const char *port) {
    struct addrinfo hints, *res, *rp;
    int fd = -1;
    int rc;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if ((rc = getaddrinfo(host, port, &hints, &res)) != 0) {
        printf("getaddrinfo: %s\n", gai_strerror(rc));
        return -1;
    }

    for (rp = res; rp != NULL; rp = rp->ai_next) {
        fd = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (fd == -1) continue;

        if (connect(fd, rp->ai_addr, rp->ai_addrlen) == 0) {
            break; // connected
        }

        close(fd);
        fd = -1;
    }

    freeaddrinfo(res);
    return fd;
}

// ========================= Menu ==========================
void menu() {
    printf("\ncommands:\n");
    printf(" c 500      reserve 500 1M blocks with calloc\n");
    printf(" f          free last reserved buffer\n");
    printf(" w 1000     write 1000 times at random pos to buffer\n");
    printf(" l 10       loop cpu with 10 times 1 mio x=sin(x)\n");
    printf(" t 5        loop cpu with 5 threads, each %d times 1 mio x=sin(x)\n", cpu_loop_cnt);
    printf(" n 9999     TCP connect to localhost port 9999\n");
    printf(" e          end program\n");
    printf("enter command:");
}

// ========================= Main ==========================
int main()
{
    size_t n, bsize=0,pos;
    char *buffer=NULL;
    while(1)
    {
        menu();
        char command;
        char zeile[100];
        fgets(zeile,99,stdin);
        sscanf(zeile,"%c %ld", &command , &n);
        char *l;
        int j;
        switch ( command)
        {  
           case 'c' :
             buffer=calloc(n, M);
             bsize=n;
             printf("%5ld 1M Bloecke reserviert ab Adresse: %p\n",n,buffer);
             printf("                           bis Adresse: %p\n",buffer+n*M);
            break;

           case 'w':
           case 'W':
            if(!buffer) { printf("No buffer allocated!\n"); break; }
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
             if(buffer) { free(buffer); buffer=NULL; bsize=0; }
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

           case 'n': {
             char portstr[32];
             sprintf(portstr, "%ld", n);
             printf("Connecting to localhost:%s …\n", portstr);
             int fd = tcp_connect("127.0.0.1", portstr);
             if (fd < 0) {
                 printf("TCP connection failed.\n");
                 break;
             }
             printf("Connected.\n");
             const char *msg = "Hello from os_from_c client!\n";
             write(fd, msg, strlen(msg));
             char buf[512];
             int r = read(fd, buf, sizeof(buf)-1);
             if (r > 0) {
                 buf[r] = '\0';
                 printf("Received: %s\n", buf);
             } else {
                 printf("No data received or connection closed.\n");
             }
             close(fd);
             break;
           }

           case 'e':
                 return(0);
        }
    }
    return 0;
}
