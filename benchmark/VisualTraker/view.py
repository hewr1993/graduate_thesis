#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat 19 Dec 2015 05:40:59 PM CST
# Purpose: view data with boxes
# Mail: hewr2010@gmail.com
import cv2
import numpy as np
import os
import sys
import glob
import time
import itertools

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(dest="dir", help="data directory")
parser.add_argument("--delay", default=40, type=int,
                    help="display delay for cv2.waitKey")
args = parser.parse_args()


def process_line(line):
    if line.find(",") >= 0:
        return map(int, line.split(","))
    else:
        return map(int, line.split("\t"))

if __name__ == "__main__":
    color = (255, 0, 0)
    thickness = 3
    img_paths = sorted(glob.glob(os.path.join(args.dir, "img/*.jpg")))
    cnt_imgs = len(img_paths)
    st_time = time.time()
    for idx, (line, img_path) in enumerate(itertools.izip(
            open(os.path.join(args.dir, "groundtruth_rect.txt")),
            img_paths,
    )):
        x, y, w, h = process_line(line.strip())
        img = cv2.imread(img_path)
        cv2.line(img, (x, y), (x + w, y), color, thickness)
        cv2.line(img, (x + w, y), (x + w, y + w), color, thickness)
        cv2.line(img, (x + w, y + w), (x, y + w), color, thickness)
        cv2.line(img, (x, y + w), (x, y), color, thickness)
        cv2.imshow('img', img)
        if chr(cv2.waitKey(args.delay) & 0xFF) == 'q':
            exit()
        print "\r%d/%d, ETA:%2.fs" % (
            idx + 1, cnt_imgs,
            (time.time() - st_time) / (idx + 1) * (cnt_imgs - idx - 1),
        ),
        sys.stdout.flush()
