#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Dec 26 12:33:53 2015
# Mail: hewr2010@gmail.com
import os
import sys
import cv2
import time
import glob
from alov_reader import load_annotations

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(dest="annotation_file", type=str)
parser.add_argument("--width", default=400, type=int)
parser.add_argument("--height", default=300, type=int)
parser.add_argument("--auto-play", action="store_true")
args = parser.parse_args()
args.delay = 1 if args.auto_play else 0

# get images directory
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
def get_images_directory(ann_fn):
    name = os.path.splitext(os.path.basename(ann_fn))[0]
    i = name.find("_")
    return os.path.join(
        BASE_DIR, "imagedata++",
        name[:i], name,
    )

args.img_dir = get_images_directory(args.annotation_file)

if __name__ == "__main__":
    anns = load_annotations(args.annotation_file)
    sum_time = 0
    for f_idx, coords in anns:
        st_time = time.time()
        base_img = cv2.imread(os.path.join(args.img_dir, "%08d.jpg" % f_idx))
        img = cv2.resize(base_img, (args.width, args.height))
        ss = (float(img.shape[1]) / base_img.shape[1],
              float(img.shape[0]) / base_img.shape[0])  # size scale
        coords = [(int(x * ss[0]), int(y * ss[1])) for x, y in coords]
        for i in xrange(len(coords)):
            p, q = coords[i], coords[(i + 1) % len(coords)]
            cv2.line(img, p, q, (0, 0, 255), 1)
        #cv2.putText(
            #img, "frame %d" % f_idx,
            #(0, 0), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
            #0.5, (128, 0, 128), 1,
        #)
        sum_time += time.time() - st_time
        print "\r%d-%d, %dx%d, %.2ffps" % (
            f_idx, anns[-1][0],
            base_img.shape[0], base_img.shape[1],
            (f_idx - anns[0][0] + 1) / sum_time,
        ),
        sys.stdout.flush()
        cv2.imshow('img', img)
        if chr(cv2.waitKey(args.delay) & 0xFF) == 'q':
            exit()
