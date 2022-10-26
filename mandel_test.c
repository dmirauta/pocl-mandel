#include <stdio.h>
#include <stdbool.h>

#include "mandelstructs.c"
#include "mandel.c"

const FPN RE0 = -2;
const FPN RE1 = 0.5;
const FPN IM0 = -1;
const FPN IM1 = 1;

const N = 30;
const M = 80;
const MAXITER = 80;

int main()
{
    int res_g[M*N];

    for(int i=0; i<N; i++)
    {
        for(int j=0; j<M; j++)
        {
            Complex_t c;

            c.re = RE0 + j*(RE1-RE0)/M;
            c.im = IM0 + i*(IM1-IM0)/N;

            res_g[i*M+j] = _escape_iter(c, c, MAXITER);
        }
    }

    for(int i=0; i<N; i++)
    {
        for(int j=0; j<M; j++)
        {
            if(res_g[i*M+j] < MAXITER)
            {
                printf(" ");
            } else {
                printf("x");
            }
        }
        printf("\n");
    }

    return 0;

}
