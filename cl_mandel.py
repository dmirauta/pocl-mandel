#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 18:50:12 2022

@author: d
"""

import os, time, ctypes, struct
import numpy as np
import pyopencl as cl
from matplotlib import pyplot as plt

os.environ["PYOPENCL_COMPILER_OUTPUT"] = "1"

mf = cl.mem_flags
ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

with open("mandelstructs.c", "r") as f:
    mandelstructs_c = f.read()

with open("mandel.c", "r") as f:
    mandel_c = f.read()

with open("mandel.cl", "r") as f:
    mandel_cl = f.read()

build_options=""

use_float=False
if use_float:
    np_fpn = np.float32
    c_fpn = ctypes.c_float
    struct_float_char="f"
    build_options += " -D USE_FLOAT"
else:
    np_fpn = np.float64
    c_fpn = ctypes.c_double
    struct_float_char="d"

print(build_options)

prg = cl.Program(ctx, mandelstructs_c+mandel_c+mandel_cl).build(options=build_options)

def gpu_fractal(view_rect,
                max_iter, N, M,

                c=None,

                prox_type=0,
                orbit_trap=False,
                trap=[-0.5, 0, -0.25, 0.25] ):

    # kernel call
    mandel = c is None
    if c is None:
        c = (0.0, 0.0)

    c_c = struct.pack("="+struct_float_char*2, *c)
    view_rect_c = struct.pack("="+struct_float_char*4, *view_rect)

    if orbit_trap: # returns coords in specified box, as soon as entered
        res_g = cl.Buffer(ctx, mf.WRITE_ONLY, ctypes.sizeof(c_fpn)*N*M*2)
        trap_c = struct.pack("="+struct_float_char*4, *trap)
        prg.orbit_trap(queue, (N,M), None,
                        res_g,
                        ctypes.c_int(mandel),
                        c_c,
                        view_rect_c,
                        trap_c,
                        ctypes.c_int(max_iter))
        res_np = np.zeros( (N,M,2), dtype=np_fpn )
    elif prox_type>0: # returns measure of proximity from various simple objects
        res_g = cl.Buffer(ctx, mf.WRITE_ONLY, ctypes.sizeof(c_fpn)*N*M)
        prg.min_prox(queue, (N,M), None,
                        res_g,
                        ctypes.c_int(mandel),
                        c_c,
                        view_rect_c,
                        ctypes.c_int(max_iter),
                        ctypes.c_int(prox_type))
        res_np = np.zeros( (N,M), dtype=np_fpn )
    else: # returns iterations to escape
        res_g = cl.Buffer(ctx, mf.WRITE_ONLY, ctypes.sizeof(c_fpn)*N*M)
        prg.escape_iter(queue, (N,M), None,
                        res_g,
                        ctypes.c_int(mandel),
                        c_c,
                        view_rect_c,
                        ctypes.c_int(max_iter))
        res_np = np.zeros( (N,M), dtype=np_fpn )


    # fetch result

    cl.enqueue_copy(queue, res_np, res_g)

    return res_np

def map_img(res_np, img="imgs/IMG_0024.JPG"):
    img_np = plt.imread(img).astype("uint8")[:,:,:3].copy()
    imh, imw, imd = img_np.shape
    N,M, _=res_np.shape

    if imd<3:
        raise Exception("Unexpected sample image depth")

    res_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=res_np)
    sim_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img_np)
#    mim_g = cl.Buffer(ctx, mf.WRITE_ONLY, ctypes.sizeof(ctypes.c_uint8)*N*M*3)

    mim_np = 255*np.ones( (N,M,3), dtype=np.uint8 )
    mim_g = cl.Buffer(ctx, mf.WRITE_ONLY | mf.COPY_HOST_PTR, hostbuf=mim_np)

    #print(res_np.shape, img.shape)
    #exit()

    prg.map_img(queue, (N,M), None,
                    res_g,
                    sim_g,
                    mim_g,
                    ctypes.c_int(imh),
                    ctypes.c_int(imw))

    cl.enqueue_copy(queue, mim_np, mim_g)

    return mim_np

def map_img_cpu(res_np):
    OTRE, OTIM = res_np[:,:,0], res_np[:,:,1]

    img = plt.imread("imgs/test.jpg")

    h,w=OTRE.shape
    imh, imw, imd = img.shape

    nan_mask = np.isnan(OTRE)
    OTRE[nan_mask]=0
    OTIM[nan_mask]=0

    OTRE_MI, OTRE_MA = OTRE.max(), OTRE.min()
    OTIM_MI, OTIM_MA = OTIM.max(), OTIM.min()

    D_RE = (OTRE_MA-OTRE_MI)/imw
    D_IM = (OTIM_MA-OTIM_MI)/imh

    res = np.zeros( (height, width, imd) )

    eps=1e-9
    for i in range(h):
        for j in range(w):
            if not nan_mask[i,j]:
                ij = int( (OTRE[i,j]+eps-OTRE_MI)/D_RE )
                ii = int( (OTIM[i,j]+eps-OTIM_MI)/D_IM )
                res[i, j, :] = img[ii, ij, :]
            else:
                res[i, j, :] = img[0, 0, :]

    return res.astype("int")


if __name__=="__main__":
    import time

    #extent = re0, re1, im0, im1 = -2, 2, -2, 2
    extent = re0, re1, im0, im1 = -2, 0.5, -1, 1
    # extent = re0, re1, im0, im1 = -0.1, 1.3, -1, 0.4
    max_iter, height, width = 500, 1080, 1920
    #c=(-0.4, 0.6)
    c=None

    t0 = time.time()
    res = gpu_fractal(extent,
                      max_iter, height, width, c=c, prox_type=2, orbit_trap=True)#, c=(-0.4, 0.6))
    print(time.time()-t0, "fractal iter")

    #plt.imshow(np.log(res), interpolation="none", cmap="nipy_spectral", origin='lower', extent=extent)
    #plt.show()

    t0 = time.time()
    resg = map_img(res)
    print(time.time()-t0, "map img gpu")

    #t0 = time.time()
    #resc = map_img_cpu(res)
    #print(time.time()-t0, "map img cpu")

    #f,(aa,ab)=plt.subplots(1,2)
    #aa.imshow(resg, interpolation="none", origin='lower', extent=extent)
    #ab.imshow(resc, interpolation="none", origin='lower', extent=extent)
    plt.imshow(resg, interpolation="none", origin='lower', extent=extent)

    plt.show()


