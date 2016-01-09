#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Jan  9 23:20:47 2016
# Purpose: token maker
# Mail: hewr2010@gmail.com
import os
import glob

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def get_images_directory(ann_fn):
    name = os.path.splitext(os.path.basename(ann_fn))[0]
    i = name.find("_")
    return os.path.join(
        os.path.dirname(ann_fn), "../../imagedata++",
        name[:i], name,
    )


def get_tokens():
    return glob.glob(os.path.join(BASE_DIR, "alov300++_rectangleAnnotation_full/*/*.ann"))

if __name__ == "__main__":
    print get_tokens()
