#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 02:15:58 2016
# Purpose: tools for drawing
# Mail: hewr2010@gmail.com
import cv2


def draw_polygon(img, coords,
                 color=(0, 0, 255), thickness=1):
    """
    @type coords: [(w, h), ...]
    """
    if isinstance(coords[0][0], float):
        coords = [(int(x * img.shape[1]), int(y * img.shape[0]))
                  for x, y in coords]
    for i in xrange(len(coords)):
        p, q = coords[i], coords[(i + 1) % len(coords)]
        cv2.line(img, p, q, color, thickness)
