#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 01:08:51 2016
# Purpose: download data from VisualTrackerBenchmark
# Mail: hewr2010@gmail.com
import os

if __name__ == "__main__":
    for line in open("./list.txt"):
        url = line.strip()
        fn = url.split("/")[-1]
        name = os.path.splitext(fn)[0]
        if not os.path.exists(name):
            os.system("wget %s" % url)
            os.system("unzip %s" % fn)
            os.system("rm %s" % fn)
