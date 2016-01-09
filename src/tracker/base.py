#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 01:59:44 2016
# Purpose: basic tracker class
# Mail: hewr2010@gmail.com
from abc import ABCMeta, abstractmethod


class Tracker(object):
    """object tracker (only for single object currently)
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def track(self, frame):
        """return bounding box(es) of tracking object(s)
        @type frame: cv2 np.ndarray
        """


class NaiveTracker(Tracker):
    def __init__(self, first_frame, bounding_box):
        """
        @type bounding_box: [(w, h), ...] for 4 corners
        """
        self.bounding_box = bounding_box

    def track(self, frame):
        return self.bounding_box
