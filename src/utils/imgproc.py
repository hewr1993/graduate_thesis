#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 16:14:07 2016
# Purpose: image processing tools
# Mail: hewr2010@gmail.com
from misc import list2nparray
import cv
import cv2
import numpy as np


def ensure_ic01(img, nr_channels):
    assert nr_channels in [1, 3], nr_channels

    if img.ndim == 3 and img.shape[-1] == 1:
        img = img.reshape(img.shape[:2])
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    assert img.ndim == 3, img.ndim

    if nr_channels == 3:
        return i01c_to_ic01(img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img_gray.reshape(-1, *img_gray.shape)


def ensure_grayscale(img):
    if img.ndim == 2:
        return img
    if img.ndim == 3: # 01c
        if img.shape[-1] == 1:
            return img.reshape(img.shape[:2][::-1])
        if img.shape[-1] == 3:
            return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        if img.shape[-1] == 4:
            return cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

    raise RuntimeError('unrecognized shape of image: {}'.format(img.shape))


def rgb2gray(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def rgba2gray(img):
    return cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)


def rgba2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


def gray2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)


def ensure_rgb(img):
    if img.ndim == 2:
        return gray2rgb(img)

    if img.ndim == 3:  # (0, 1, c)
        if img.shape[-1] == 1:
            return gray2rgb(img.reshape(img.shape[:2]))
        if img.shape[-1] == 3:
            return img
        if img.shape[-1] == 4:
            return rgba2rgb(img)

    raise RuntimeError('unrecognized shape of image: {}'.format(img.shape))


def list2nparray(lst, dtype=None):
    """fast conversion from nested list to ndarray by pre-allocating space"""
    if isinstance(lst, np.ndarray):
        return lst
    assert isinstance(lst, (list, tuple)), 'bad type: {}'.format(type(lst))
    assert lst, 'attempt to convert empty list to np array'
    if isinstance(lst[0], np.ndarray):
        dim1 = lst[0].shape
        assert all(i.shape == dim1 for i in lst), [i.shape for i in lst]
        if dtype is None:
            dtype = lst[0].dtype
            assert all(i.dtype == dtype for i in lst), (dtype, [i.dtype for i in lst])
    elif isinstance(lst[0], (int, float, long, complex)):
        return list2nparray(lst, dtype=dtype)
    else:
        dim1 = list2nparray(lst[0])
        if dtype is None:
            dtype = dim1.dtype
        dim1 = dim1.shape
    shape = [len(lst)] + list(dim1)
    rst = np.zeros(shape, dtype=dtype)
    for idx, i in enumerate(lst):
        rst[idx] = i
    return rst


def i01c_to_ic01(arr, allow_2d=False, out_4d=False):
    """change array of axis (0, 1, 'c') to ('c', 0, 1)"""
    arr = list2nparray(arr)
    if allow_2d and arr.ndim == 2:
        arr = arr.reshape((arr.shape[0], arr.shape[1], 1))
    assert arr.ndim == 3 and arr.shape[2] in (1, 3), arr.shape
    arr = np.rollaxis(arr, 2)
    if out_4d:
        arr = arr.reshape((1, arr.shape[0], arr.shape[1], arr.shape[2]))
    return arr


def ic01_to_i01c(arr, allow_2d=False):
    """change array of axis ('c', 0, 1) to (0, 1, 'c')"""
    arr = list2nparray(arr)
    if allow_2d and arr.ndim == 2:
        arr = arr.reshape((1, arr.shape[0], arr.shape[1]))
    assert arr.ndim == 3 and arr.shape[0] in (1, 3), arr.shape
    return np.swapaxes(np.rollaxis(arr, 1), 1, 2)


def normalized_histogram(img):
    if img.ndim == 2:  # grayscale
        hist = cv2.calcHist([img], [0], None, [256], [0., 255.0])
        return cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    else:
        hists = []
        for channel in xrange(img.shape[2]):
            hist = cv2.calcHist([img], [channel], None, [256], [0., 255.0])
            hists.append(cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX))
        return list2nparray(hists)


def histogram_similarity(img0, img1, method=cv.CV_COMP_INTERSECT):
    """
    @type method:
        CV_COMP_CORREL Correlation
        CV_COMP_CHISQR Chi-Square
        CV_COMP_INTERSECT Intersection
        CV_COMP_BHATTACHARYYA Bhattacharyya distance
        CV_COMP_HELLINGER Synonym for CV_COMP_BHATTACHARYYA
    """
    hist0 = normalized_histogram(img0)
    hist1 = normalized_histogram(img1)
    return cv2.compareHist(hist0, hist1, method)


def matting_by_color_range(img, color_low=None, color_high=None):
    """convert rgb to rgba by setting color in [low, high] transparent
    """
    assert img.ndim == 3 and img.shape[2] == 3
    assert color_low is not None or color_high is not None
    color_low = np.array((0,) * 3 if color_low is None else color_low)
    color_high = np.array((255,) * 3 if color_high is None else color_high)
    assert color_low.shape == (3,) and color_high.shape == (3,)
    mask = 1 - ((img >= color_low) & (img <= color_high)).all(axis=2)\
        .astype("float32")
    nimg = np.zeros(img.shape[:2] + (4,), 'uint8')
    nimg[:, :, :3] = img
    nimg[:, :, 3] = (mask * 255).astype('uint8')
    return nimg
