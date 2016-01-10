#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 16:35:40 2016
# Purpose: vector related functions
# Mail: hewr2010@gmail.com
import math
import numpy as np
from misc import list2nparray


def normalize(v):
    v = list2nparray(v)
    _min, _max = min(v), max(v)
    v -= _min
    if sum(v) == 0:
        return np.ones(v.shape, 'float32') / np.prod(v.shape)
    return v / sum(v)


def cosine_similarity(v0, v1):
    a, b = list2nparray(v0, "float32"), list2nparray(v1, "float32")
    return np.dot(a, b) / math.sqrt(sum(a ** 2)) / math.sqrt(sum(b ** 2))
