#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Jan  9 23:24:12 2016
# Purpose: load data given tokens
# Mail: hewr2010@gmail.com
import os
import cv2
import glob
import random
from token import get_tokens, get_images_directory


def ensure_coordinates_order(coords):
    ul, br = min(coords), max(coords)
    while coords[0] != ul:
        coords = coords[1:] + coords[:1]
    if coords[1][1] >= coords[-1][1]:
        coords = list(reversed(coords))
        coords = coords[-1:] + coords[:-1]
    return coords


def load_annotations(ann_fn):
    raw = []
    for line in open(ann_fn):
        arr = line.strip().split(" ")
        idx = int(arr[0])
        coords = map(float, arr[1:])
        raw.append((idx, coords))
    for i in xrange(1, len(raw)):
        (f1_idx, coords1), (f2_idx, coords2) = raw[i - 1], raw[i]
        steps = [(r - l) / (f2_idx - f1_idx) for l, r in zip(coords1, coords2)]
        for j in xrange(f2_idx - f1_idx):
            f_idx = f1_idx + j
            coords = [int(x + s * j) for x, s in zip(coords1, steps)]
            coords = zip(coords[::2], coords[1::2])
            coords = ensure_coordinates_order(coords)
            yield (f_idx, coords)


def load_given_tokens(tokens=None, randomize=True):
    """
    @param tokens: None for loading all instances
    @type tokens: list(str)
    @return: (token, data_stream)
    """
    def get_data_stream(token):
        """
        @return: [(img, (4 coordinates))]
        """
        img_dir = get_images_directory(token)
        for f_idx, coords in load_annotations(token):
            img = cv2.imread(os.path.join(img_dir, "%08d.jpg" % f_idx))
            coords = [(float(x) / img.shape[1], float(y) / img.shape[0])
                      for x, y in coords]
            yield (img, coords)

    if tokens is None:
        tokens = get_tokens()
    if randomize:
        random.shuffle(tokens)
    for token in tokens:
        yield (token, get_data_stream(token))


def get_length_by_token(token):
    lines = [l for l in open(token)]
    begin = int(lines[0].split(" ")[0])
    end = int(lines[-1].split(" ")[0])
    return end - begin + 1

if __name__ == "__main__":
    for token, data_stream in load_given_tokens():
        print token
        for img, coords in data_stream:
            coords = [(int(x * img.shape[1]), int(y * img.shape[0]))
                      for x, y in coords]
            for i in xrange(len(coords)):
                p, q = coords[i], coords[(i + 1) % len(coords)]
                cv2.line(img, p, q, (0, 0, 255), 1)
            cv2.imshow('img', img)
            if chr(cv2.waitKey(0) & 0xFF) == 'q':
                exit()
