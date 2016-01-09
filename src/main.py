#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 01:57:25 2016
# Purpose: main process for object tracking
# Mail: hewr2010@gmail.com
from benchmark import get_instances
from tracker import *

if __name__ == "__main__":
    tracker = Tracker()
    for token, data_stream in get_instances():
        print token
        break
