#ifdef USE_FLOAT
    typedef float FPN;
#else
    typedef double FPN;
#endif

typedef struct Complex {
    FPN re;
    FPN im;
} Complex_t;

typedef struct Box {
    FPN left;
    FPN right;
    FPN bot;
    FPN top;
} Box_t;

typedef struct Pixel {
   unsigned char r; // equivalent of uint8 in opencl...
   unsigned char g;
   unsigned char b;
} Pixel_t;
