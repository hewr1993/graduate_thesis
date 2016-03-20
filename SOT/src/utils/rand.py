#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 14:02:39 2016
# Purpose: randomize related
# Mail: hewr2010@gmail.com
import random


def noise(level, x=0):
    return x + random.uniform(-level, level)
