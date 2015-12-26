#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Dec 26 15:30:59 2015
# Purpose: make structured data
# Mail: hewr2010@gmail.com
import cv2
import os
import glob

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def load_annotations(ann_fn):
    raw = []
    for line in open(ann_fn):
        arr = line.strip().split(" ")
        idx = int(arr[0])
        coords = map(float, arr[1:])
        raw.append((idx, coords))
    anns = []
    for i in xrange(1, len(raw)):
        (f1_idx, coords1), (f2_idx, coords2) = raw[i - 1], raw[i]
        steps = [(r - l) / (f2_idx - f1_idx) for l, r in zip(coords1, coords2)]
        for j in xrange(f2_idx - f1_idx):
            f_idx = f1_idx + j
            coords = [int(x + s * j) for x, s in zip(coords1, steps)]
            coords = zip(coords[::2], coords[1::2])
            anns.append((f_idx, coords))
    return anns
