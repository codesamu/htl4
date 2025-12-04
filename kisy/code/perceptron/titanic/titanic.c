
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N_FEATURES 7
#define MAX_SAMPLES 3000   /* adjust if needed */

/* Data structure for one sample */
typedef struct {
    double x[N_FEATURES];  /* features */
    int y;                 /* label 0 or 1 */
} Sample;

/* Load numeric dataset: each line: 7 features + 1 label */
int load_dataset(const char *filename, Sample *data) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        perror("fopen");
        return -1;
    }

    int count = 0;
    while (!feof(f) && count < MAX_SAMPLES) {
        double f0, f1, f2, f3, f4, f5, f6;
        int label;
        int n = fscanf(f, "%lf %lf %lf %lf %lf %lf %lf %d",
                       &f0, &f1, &f2, &f3, &f4, &f5, &f6, &label);
        if (n == 8) {
            data[count].x[0] = f0;
            data[count].x[1] = f1;
            data[count].x[2] = f2;
            data[count].x[3] = f3;
            data[count].x[4] = f4;
            data[count].x[5] = f5;
            data[count].x[6] = f6;
            data[count].y = label;
            count++;
        } else {
            /* Skip bad/empty line */
            char buf[1024];
            if (!fgets(buf, sizeof(buf), f))
                break;
        }
    }

    fclose(f);
    return count;
}

/* Shuffle indices array in-place */
void shuffle_indices(int *indices, int n) {
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = indices[i];
        indices[i] = indices[j];
        indices[j] = tmp;
    }
}

/* Perceptron prediction for one sample */
int perceptron_predict_one(const double *x, const double *w) {
    double y_val = w[0]; /* bias */
    for (int i = 0; i < N_FEATURES; i++) {
        y_val += w[i + 1] * x[i];
    }
    return (y_val > 0.0) ? 1 : 0;
}

/* Accuracy on a set of samples */
double accuracy(Sample *data, int *indices, int n_idx, const double *w) {
    int correct = 0;
    for (int k = 0; k < n_idx; k++) {
        int i = indices[k];
        int pred = perceptron_predict_one(data[i].x, w);
        if (pred == data[i].y) {
            correct++;
        }
    }
    return (double)correct / (double)n_idx;
}

/* Perceptron training with early stopping on target test accuracy */
void perceptron_train(
    Sample *data,
    int *train_idx, int n_train,
    int *test_idx,  int n_test,
    int max_epochs,
    double alpha,
    double target_acc
) {
    double w[N_FEATURES + 1];  /* bias + weights */
    for (int i = 0; i < N_FEATURES + 1; i++) {
        w[i] = 0.0;
    }

    for (int epoch = 0; epoch < max_epochs; epoch++) {
        /* Shuffle training indices each epoch */
        shuffle_indices(train_idx, n_train);

        /* SGD-like training */
        for (int k = 0; k < n_train; k++) {
            int idx = train_idx[k];
            Sample *s = &data[idx];

            double y_val = w[0]; /* bias */
            for (int i = 0; i < N_FEATURES; i++) {
                y_val += w[i + 1] * s->x[i];
            }
            int pred = (y_val > 0.0) ? 1 : 0;
            int error = s->y - pred;  /* -1, 0, or 1 */

            if (error != 0) {
                /* update bias */
                w[0] += alpha * error * 1.0;
                /* update weights */
                for (int i = 0; i < N_FEATURES; i++) {
                    w[i + 1] += alpha * error * s->x[i];
                }
            }
        }

        double train_acc = accuracy(data, train_idx, n_train, w);
        double test_acc  = accuracy(data, test_idx,  n_test,  w);

        printf("Epoch %d: train=%.4f, test=%.4f\n",
               epoch + 1, train_acc, test_acc);

        if (test_acc >= target_acc) {
            printf("Reached target test accuracy, stopping.\n");
            printf("Final train accuracy: %.4f\n", train_acc);
            printf("Final test  accuracy: %.4f\n", test_acc);
            printf("Final weights:\n");
            for (int i = 0; i < N_FEATURES + 1; i++) {
                printf("w[%d] = %.6f\n", i, w[i]);
            }
            return;
        }
    }

    /* If we exit loop without reaching target, still print final stats */
    double train_acc = accuracy(data, train_idx, n_train, w);
    double test_acc  = accuracy(data, test_idx,  n_test,  w);
    printf("Stopped after max_epochs.\n");
    printf("Final train accuracy: %.4f\n", train_acc);
    printf("Final test  accuracy: %.4f\n", test_acc);
    printf("Final weights:\n");
    for (int i = 0; i < N_FEATURES + 1; i++) {
        printf("w[%d] = %.6f\n", i, w[i]);
    }
}

int main(void) {
    const char *filename = "titanic_numeric.txt";
    Sample data[MAX_SAMPLES];

    srand((unsigned)time(NULL));

    int n = load_dataset(filename, data);
    if (n <= 0) {
        fprintf(stderr, "Failed to load dataset or empty dataset.\n");
        return 1;
    }

    printf("Loaded %d samples.\n", n);

    /* Build index array [0..n-1] and shuffle */
    int *indices = (int *)malloc(n * sizeof(int));
    if (!indices) {
        perror("malloc");
        return 1;
    }
    for (int i = 0; i < n; i++) {
        indices[i] = i;
    }
    shuffle_indices(indices, n);

    /* Train/test split: test_ratio = 0.2 */
    double test_ratio = 0.2;
    int split = (int)(n * (1.0 - test_ratio));
    int n_train = split;
    int n_test  = n - split;

    int *train_idx = (int *)malloc(n_train * sizeof(int));
    int *test_idx  = (int *)malloc(n_test  * sizeof(int));
    if (!train_idx || !test_idx) {
        perror("malloc");
        return 1;
    }

    for (int i = 0; i < n_train; i++) {
        train_idx[i] = indices[i];
    }
    for (int i = 0; i < n_test; i++) {
        test_idx[i] = indices[split + i];
    }

    int max_epochs = 100000000;
    double alpha = 0.01;
    double target_acc = 0.84;

    perceptron_train(
        data,
        train_idx, n_train,
        test_idx,  n_test,
        max_epochs,
        alpha,
        target_acc
    );

    free(indices);
    free(train_idx);
    free(test_idx);

    return 0;
}
