#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Dec 27 01:42:18 2015
# Mail: hewr2010@gmail.com
import os
import sys
import cv2
import time
import glob

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(dest="dir", type=str, help="data directory")
args = parser.parse_args()

if __name__ == "__main__":
    ann_fn = os.path.join(args.dir, "groundtruth.txt")
    cnt = len(glob.glob(os.path.join(args.dir, "*.jpg")))
    sum_time = 0
    for idx, line in enumerate(open(ann_fn)):
        st_time = time.time()
        arr = map(int, map(float, line.strip().split(",")))
        coords = zip(arr[::2], arr[1::2])
        img = cv2.imread(os.path.join(args.dir, "%08d.jpg" % (idx + 1)))
        for i in xrange(len(coords)):
            p, q = coords[i], coords[(i + 1) % len(coords)]
            cv2.line(img, p, q, (0, 0, 255), 1)
        sum_time += time.time() - st_time
        print "\r%d/%d, %.2ffps" % (
            idx + 1, cnt,
            (idx + 1) / sum_time,
        ),
        sys.stdout.flush()
        cv2.imshow('img', img)
        if chr(cv2.waitKey(0) & 0xFF) == 'q':
            exit()
