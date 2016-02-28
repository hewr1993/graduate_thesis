#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Mon 16 Nov 2015 05:44:50 PM CST
# Purpose: import all modules
# Mail: hewr2010@gmail.com
from importlib import import_module
from pkgutil import walk_packages
import os


def import_all_modules(file_path, pkg_name, import_to_globals=None):
    """import all modules recursively in a package
    :param file_path: just pass __file__
    :param pkg_name: just pass __name__
    :param import_to_globals: a dict of globals()
    """
    for _, module_name, _ in walk_packages(
            [os.path.dirname(file_path)], pkg_name + '.'):
        mod = import_module(module_name)
        if import_to_globals is not None:
            for key, val in mod.__dict__.iteritems():
                # print("{}.{}".format(module_name,key))
                import_to_globals[key] = val

all_modules = dict()
import_all_modules(__file__, __name__, all_modules)

locals().update(all_modules)
# vim: foldmethod=marker
