#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 01:57:25 2016
# Purpose: main process for object tracking
# Mail: hewr2010@gmail.com
import cv2
from benchmark import get_instances
from tracker import *
from utils import draw_polygon


def evaluate(tracker_type=NaiveTracker, EXTRA_CANDIDATES=0):
    """
    @param EXTRA_CANDIDATES: how many candidates should we draw
    """
    for token, data_stream in get_instances():
        print token
        results, gt_results = [], []
        for idx, (img, gt_coords) in enumerate(data_stream):
            if idx == 0:
                tracker = tracker_type(img, gt_coords)
            else:
                coords = tracker.track(img)
                results.append(coords)
                gt_results.append(gt_coords)
                draw_polygon(img, gt_coords, color=(0, 255, 0))
                draw_polygon(img, coords, color=(0, 0, 255))
                for particle in tracker.particles[:EXTRA_CANDIDATES]:
                    draw_polygon(img, particle.coords, color=(255, 0, 0))
                cv2.imshow('img', img)
                if chr(cv2.waitKey(0) & 0xFF) == 'q':
                    exit()
        # TODO evaluate results

if __name__ == "__main__":
    evaluate(ParticleFilterTracker)
