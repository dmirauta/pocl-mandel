#include <stdio.h>
#include <stdbool.h>

#include "mandel.c"
//int remains_in_bounds(struct Complex z, struct Complex c);

const FPN RE0 = -2;
const FPN RE1 = 0.5;
const FPN IM0 = -1;
const FPN IM1 = 1;

int main()
{
    int res_g[M*N];

    for(int i=0; i<N; i++)
    {
        for(int j=0; j<M; j++)
        {
            struct Complex c;

            c.re = RE0 + j*(RE1-RE0)/M;
            c.im = IM0 + i*(IM1-IM0)/N;

            res_g[i*M+j] = remains_in_bounds(c, c);
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
