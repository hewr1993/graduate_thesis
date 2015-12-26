#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Dec 26 12:33:53 2015
# Mail: hewr2010@gmail.com
import os
import sys
import cv2
import glob

from alov_reader import load_annotations

if __name__ == "__main__":
    ann_fn = "./alov300++_rectangleAnnotation_full/01-Light/01-Light_video00001.ann"
    anns = load_annotations(ann_fn)
    img_dir = "./imagedata++/01-Light/01-Light_video00001"
    for f_idx, coords in anns:
        img = cv2.imread(os.path.join(img_dir, "%08d.jpg" % f_idx))
        for i in xrange(len(coords)):
            p, q = coords[i], coords[(i + 1) % len(coords)]
            cv2.line(img, p, q, (0, 0, 255), 1)
        print "\r%d" % f_idx,
        sys.stdout.flush()
        cv2.imshow('img', img)
        if chr(cv2.waitKey(0) & 0xFF) == 'q':
            exit()
