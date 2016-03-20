#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Wed 18 Nov 2015 05:20:24 PM CST
# Purpose: misc tools
# Mail: hewr2010@gmail.com
import numpy as np


def calc_batched_size(batch_size, size):
    """example: numpy.random.RandomState.choice
    """
    if size is None:
        return (batch_size,)
    elif isinstance(size, int):
        return (batch_size, size)
    else:
        return (batch_size,) + size


def ensure_arg_type(**predicates):
    '''example:
    @ensure_arg_type(alpha=int, beta=(str, int))
    def func(alpha, beta):
        assert isinstance(alpha, int)
        assert isinstance(beta, (str, int))
        return alpha + int(beta)
    '''
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            argmap = inspect.getcallargs(func, *args, **kwargs)
            for k, typ in predicates.iteritems():
                if k in argmap:
                    assert isinstance(argmap[k], typ), (
                        'argument `{}={}\' of function `{}\' '
                        'must have type `{}\''.format(
                            k, argmap[k], func.__name__, typ))
            return func(*args, **kwargs)
        return wrapper
    return deco


def merge_dict(*args):
    d = {}
    for _d in args:
        d.update(_d)
    return d


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
        return np.array(lst, dtype=dtype)
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


def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        ret = func(*args, **kwargs)
        duration = time.time() - start_time

        if hasattr(func, '__name__'):
            func_name = func.__name__
        else:
            func_name = 'function in module {}'.format(func.__module__)

        logger.info('Duration for `{}\': {}'.format(
            func_name, duration))

        return ret

    return wrapper
