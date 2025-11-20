#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

const size_t M = 1024 * 1024;

int cpu_loop_cnt = 100;

void burn_cpu(int ntimes) {
    int j;
    double x = 2;
    printf("... cpu loop %d Mio times x=sin(x)\n", ntimes);
    for (j = 0; j < ntimes; j++) {
        for (size_t i = 0; i < M; i++) {
            x = sin(x);
        }
    }
}

void my_thread(void *ptr) {
    burn_cpu(cpu_loop_cnt);
}

void thread_test(int n) {
    pthread_t thp[100];
    if (n > 99) n = 99;
    for (int i = 0; i < n; i++) {
        if (pthread_create(&thp[i], NULL, (void *) &my_thread, NULL))
            perror("could not create thread");
    }
    for (int i = 0; i < n; i++) {
        pthread_join(thp[i], NULL);
    }
}

void menu() {
    printf("\ncommands:\n");
    printf(" c 500      reserve 500 1M blocks with calloc\n");
    printf(" f          free last reserved buffer\n");
    printf(" w 1000     write 1000 times at random pos to buffer\n");
    printf(" r filename read buffer from file\n");
    printf(" s filename write buffer to file\n");
    printf(" l 10       loop cpu with 10 times 1 mio x=sin(x)\n");
    printf(" t 5        loop cpu with 5 threads, each %d times 1 mio x=sin(x)\n", cpu_loop_cnt);
    printf(" e          end program\n");
    printf("enter command:");
}

int main() {
    size_t n, bsize = 0, pos;
    char *buffer = NULL;
    while (1) {
        menu();
        char command;
        char zeile[200];
        if (!fgets(zeile, sizeof(zeile), stdin)) break;
        // für 's' und 'r' brauchen wir evtl String-Argument
        // sscanf kann bis zu zwei Argumente lesen
        char filename[128];
        int args = sscanf(zeile, "%c %ld %127s", &command, &n, filename);
        int j;
        switch (command) {
        case 'c':
            buffer = calloc(n, M);
            if (!buffer) {
                perror("calloc failed");
                break;
            }
            bsize = n;
            printf("%5ld 1M Blocks reserved at %p\n", n, (void*)buffer);
            printf("                           until %p\n", (void*)(buffer + n * M));
            break;

        case 'w':
        case 'W':
            if (!buffer) {
                printf("No buffer allocated. Use 'c' first.\n");
                break;
            }
            printf("fill %ld times a random position with 1MByte of 0xff\n", n);
            for (j = 0; j < (int)n; j++) {
                pos = M * (rand() % bsize);
                char *l = buffer + pos;
                if (command == 'W')
                    printf("write at offset %10zu %p \n", pos, l);
                for (size_t i = 0; i < M; i++) *(l++) = (char)0xff;
            }
            break;

        case 'f':
            free(buffer);
            buffer = NULL;
            bsize = 0;
            break;

        case 's': { // speichern in Datei
            if (!buffer) {
                printf("No buffer to write.\n");
                break;
            }
            if (args < 3) {
                printf("Usage: s <count> <filename>\n");
                break;
            }
            FILE *fp = fopen(filename, "wb");
            if (!fp) {
                perror("fopen for write failed");
                break;
            }
            size_t total = bsize * M;
            clock_t start = clock();
            size_t written = fwrite(buffer, 1, total, fp);
            clock_t end = clock();
            fclose(fp);
            double duration = (double)(end - start) / CLOCKS_PER_SEC;
            printf("Wrote %zu bytes in %.3f s (%.2f MB/s)\n", written, duration, (written / (1024.0*1024.0)) / duration);
            break;
        }

        case 'r': { // lesen aus Datei
            if (args < 3) {
                printf("Usage: r <count> <filename>\n");
                break;
            }
            FILE *fp = fopen(filename, "rb");
            if (!fp) {
                perror("fopen for read failed");
                break;
            }
            // wir erwarten, dass der Puffer schon angelegt ist und groß genug ist
            if (!buffer) {
                printf("No buffer allocated. Use 'c' first.\n");
                fclose(fp);
                break;
            }
            size_t total = bsize * M;
            clock_t start = clock();
            size_t read = fread(buffer, 1, total, fp);
            clock_t end = clock();
            fclose(fp);
            double duration = (double)(end - start) / CLOCKS_PER_SEC;
            printf("Read %zu bytes in %.3f s (%.2f MB/s)\n", read, duration, (read / (1024.0*1024.0)) / duration);
            break;
        }

        case 'l':
            printf("cpu loop %ld Mio times x=sin(x)\n", n);
            burn_cpu(n);
            cpu_loop_cnt = n;
            break;

        case 't':
            printf("cpu loop with %ld threads %d Mio times x=sin(x)\n", n, cpu_loop_cnt);
            thread_test(n);
            break;

        case 'e':
            return 0;

        default:
            printf("Unknown command %c\n", command);
        }
    }
    return 0;
}
