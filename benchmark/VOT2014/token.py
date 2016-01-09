#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat Jan  9 23:20:47 2016
# Purpose: token maker
# Mail: hewr2010@gmail.com
import os
import glob

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def get_images_directory(token):
    return os.path.dirname(token)


def get_tokens():
    return glob.glob(os.path.join(BASE_DIR, "*/groundtruth.txt"))

if __name__ == "__main__":
    print get_tokens()
