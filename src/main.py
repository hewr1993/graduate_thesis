#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 01:57:25 2016
# Purpose: main process for object tracking
# Mail: hewr2010@gmail.com
from tracker import *
from pipeline import *

if __name__ == "__main__":
    tracker_constructor = lambda *args, **kwargs:\
        HistogramParticleFilterTracker(*args, nr_particle=1000, **kwargs)
    worker = NormalPipeline(tracker_constructor, verbose=True)
    worker.run(display_screen=(600, 800))
