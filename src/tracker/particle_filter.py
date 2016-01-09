#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 02:07:24 2016
# Purpose: particle filter object tracker
# Mail: hewr2010@gmail.com
from base import Tracker


class ParticleFilterTracker(Tracker):
    def __init__(self, first_frame, bounding_box):
        """
        @type bounding_box: [(w, h), ...] for 4 corners
        """
        self.bounding_box = bounding_box

    def track(self, frame):
        return self.bounding_box
