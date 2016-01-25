#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 01:57:25 2016
# Purpose: main process for object tracking
# Mail: hewr2010@gmail.com
import cv2
import numpy as np
import progressbar
from benchmark import get_instances, get_length_by_token
from tracker import *
from utils import draw_polygon, fit_image_in_box


def evaluate(tracker_type=NaiveTracker, EXTRA_CANDIDATES=0,
             display_screen=(600, 800)):
    """
    @param EXTRA_CANDIDATES: how many candidates should we draw
    @param display_screen: (height, width). None for no display
    """
    for token, data_stream in get_instances():
        print token
        instance_length = get_length_by_token(token)
        widgets = [progressbar.Percentage(), " ", progressbar.Bar(), " ",
                   progressbar.Counter(format="%d" + "/%d" % instance_length)]
        pbar = progressbar.ProgressBar(maxval=instance_length, widgets=widgets)
        results, gt_results = [], []
        for idx, (img, gt_coords) in pbar(enumerate(data_stream)):
            img = fit_image_in_box(img, display_screen)
            if idx == 0:
                tracker = tracker_type(img, gt_coords)
            else:
                coords = tracker.track(img)
                results.append(coords)
                gt_results.append(gt_coords)
                board = (np.zeros(img.shape) + 255).astype('uint8')
                # plot particles
                for particle in sorted(
                        tracker.particles, key=lambda x: x.weight,
                )[:EXTRA_CANDIDATES]:
                    po = particle.center()
                    po = (int(po[0] * board.shape[1]),
                          int(po[1] * board.shape[0]))
                    cv2.circle(board, po, 1, (255, 0, 0), 1)
                # plot tracking results
                draw_polygon(img, gt_coords, color=(0, 255, 0))
                draw_polygon(img, coords, color=(0, 0, 255))
                # show results
                cv2.imshow('particles', board)
                cv2.imshow('img', img)
                keyboard = chr(cv2.waitKey(0) & 0xFF)
                if keyboard == 'q':
                    exit()
                elif keyboard == 's':
                    break
        # TODO evaluate results

if __name__ == "__main__":
    evaluate(ParticleFilterTracker, EXTRA_CANDIDATES=-1)
