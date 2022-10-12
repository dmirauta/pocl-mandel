#!/bin/env python

import sys, os
import numpy as np

from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt5 import QtGui, QtWidgets, uic


### https://gist.github.com/smex/5287589
gray_color_table = [ QtGui.qRgb(i, i, i) for i in range(256) ]
def toQImage(im, copy=False):
    if im is None:
        return QtGui.QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 2:
            qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim.copy() if copy else qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_RGB888);
                return qim.copy() if copy else qim
            elif im.shape[2] == 4:
                qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_ARGB32);
                return qim.copy() if copy else qim

    raise Exception("not implemented")
###

import time
from cl_mandel import map_img, gpu_fractal

class Window(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        uic.loadUi('mandel.ui', self)

        for f in os.listdir("imgs"):
            self.ot_img_combo.addItem(f, "imgs/"+f)

        for sb in [self.ot_bot, self.ot_top, self.ot_left, self.ot_right]:
            sb.valueChanged.connect(self.compute)

        #self.button.clicked.connect(self.compute)
        self.ot_img_combo.currentIndexChanged.connect(self.compute)

        self.compute()

    def set_image(self, im):
        self.label.setPixmap(  QtGui.QPixmap.fromImage( toQImage(im) ) )

    def compute(self):
        #extent = re0, re1, im0, im1 = -2, 2, -2, 2
        extent = re0, re1, im0, im1 = -2, 0.5, -1, 1
        # extent = re0, re1, im0, im1 = -0.1, 1.3, -1, 0.4
        max_iter, height, width = 500, 1080, 1920
        c=None

        otb = [ self.ot_left.value(),
                self.ot_right.value(),
                self.ot_bot.value(),
                self.ot_top.value() ]

        t0 = time.time()
        cres = gpu_fractal(extent,
                           max_iter, height, width,
                           orbit_trap=True,
                           trap=otb,
                           c=c)
        print(time.time()-t0, "gpu time")

        t0 = time.time()
        f = lambda im: np.sqrt(im*1.1-im.min())

        res = map_img( cres, img=self.ot_img_combo.currentData())# map_img(f(OTRE), f(OTIM))
        print(time.time()-t0, "map img")

        self.set_image( res )


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = Window()
    #widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())

