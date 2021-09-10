/* Header portion of the se programs */
#define NOTFIXED -100

#include <stdio.h>
#include <stdbool.h>

typedef enum {Py_LT, Py_LE, Py_EQ, Py_NE, Py_GT, Py_GE,
} comparisons;

#define fprintf ignore_fprintf

void fprintf(FILE *f, char *s, ...)
{
    ;
}

static bool fatal_error = false;

void Py_FatalError(char *ignored)
{
    fatal_error = true;
}
