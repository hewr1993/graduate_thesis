#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 01:59:44 2016
# Purpose: basic tracker class
# Mail: hewr2010@gmail.com
from abc import ABCMeta, abstractmethod


class Tracker(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def track(self, img):
        """return bounding box(es) of tracking object(s)
        """
