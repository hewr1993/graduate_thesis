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
        def process_line(line):
            if line.find(",") >= 0:
                return map(int, line.split(","))
            else:
                return map(int, line.split("\t"))

        img_dir = get_images_directory(token)
        for idx, line in enumerate(open(token)):
            img = cv2.imread(os.path.join(img_dir, "%04d.jpg" % (idx + 1)))
            x, y, w, h = process_line(line.strip())
            coords = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
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
    return len(list(open(token)))

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
