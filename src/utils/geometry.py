#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 02:15:58 2016
# Purpose: tools for drawing
# Mail: hewr2010@gmail.com
import cv2
import numpy as np


def ensure_relative_coordinates(coords, shape):
    """
    @type coords: [(w, h), ...]
    """
    if isinstance(coords[0][0], int):
        coords = [(float(x) / shape[1], float(y) * shape[0]) for x, y in coords]
    return coords


def ensure_absolute_coordinates(coords, shape):
    """
    @type coords: [(w, h), ...]
    """
    if isinstance(coords[0][0], float):
        coords = [(int(x * shape[1]), int(y * shape[0])) for x, y in coords]
    return coords


def draw_polygon(img, coords,
                 color=(0, 0, 255), thickness=1):
    coords = ensure_absolute_coordinates(coords, img.shape[:2])
    cv2.polylines(img, np.array([coords], 'int64'), True, color, thickness)


def get_rectangular_area(p, q):
    return (q[0] - p[0]) * (q[1] - p[1])

def get_overlap_area(coords0, coords1):
    # FIXME only support rectangular at present
    p = max(coords0[0], coords1[0])
    q = min(coords0[2], coords1[2])
    return get_rectangular_area(p, q)


def fit_image_in_box(img, screen):
    """scale in proportion to fit in screen
    @param screen: (height, width)
    """
    ratio = min(float(screen[0]) / img.shape[0],
                float(screen[1]) / img.shape[1])
    if ratio < 1.:
        img = cv2.resize(img, (int(img.shape[1] * ratio),
                               int(img.shape[0] * ratio)))
    return img
