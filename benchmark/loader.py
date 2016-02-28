#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Jan  9 20:43:12 2016
# Purpose: unified data provider
# Mail: hewr2010@gmail.com
import cv2
import random
import ALOV
import VOT2014
import VisualTracker

DATASETS = [
    ALOV,
    #VOT2014,
    VisualTracker,
]


def get_length_by_token(token):
    for ds in DATASETS:
        if ds.has_token(token):
            return ds.get_length_by_token(token)
    raise NotImplementedError


def get_instances(randomize=True):
    gnrs = [ds.load_given_tokens(randomize=randomize) for ds in DATASETS]
    while len(gnrs) > 0:
        gnr_idx = random.randint(0, len(gnrs) - 1) if randomize else 0
        try:
            gnr = gnrs[gnr_idx]
            yield gnr.next()
        except StopIteration:
            del gnrs[gnr_idx]

if __name__ == "__main__":
    for token, data_stream in get_instances():
        print token
        for img, coords in data_stream:
            coords = [(int(x * img.shape[1]), int(y * img.shape[0]))
                      for x, y in coords]
            for i in xrange(len(coords)):
                p, q = coords[i], coords[(i + 1) % len(coords)]
                cv2.line(img, p, q, (0, 0, 255), 1)
            cv2.imshow('img', img)
            key = chr(cv2.waitKey(0) & 0xFF)
            if key == 'q':
                exit()
            elif key == 's':
                break
