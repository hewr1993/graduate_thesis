#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Mar 19 17:39:59 2016
# Mail: hewr2010@gmail.com
import os
import sys
import cv2
import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--video", type=str, default="./sfz.mp4")
parser.add_argument("--max_height", type=int, default=540)
parser.add_argument("--max_width", type=int, default=960)
parser.add_argument("--save_to", type=str, default="")
args = parser.parse_args()

if args.save_to != "":
    try:
        os.makedirs(args.save_to)
    except OSError:
        pass


def get_in_box(img, max_shape):
    r_h = float(img.shape[0]) / max_shape[0]
    r_w = float(img.shape[1]) / max_shape[1]
    r = max(r_h, r_w)
    shape = (int(img.shape[0] / r), int(img.shape[1] / r))
    return cv2.resize(img, shape[::-1], interpolation=cv2.INTER_AREA)

if __name__ == "__main__":
    cap = cv2.VideoCapture(args.video)
    cnt = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        frame = get_in_box(frame, (args.max_height, args.max_width))
        # display
        cnt += 1
        print "\r", cnt, frame.shape,
        sys.stdout.flush()
        if args.save_to != "":
            cv2.imwrite(os.path.join(args.save_to, "%d.jpg" % cnt), frame)
        else:
            cv2.imshow('frame', frame)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                exit()

    cap.release()
    cv2.destroyAllWindows()
