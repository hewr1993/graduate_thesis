#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Feb 28 10:44:24 2016
# Purpose: pipeline base
# Mail: hewr2010@gmail.com
import cv2
import numpy as np
import progressbar
from abc import ABCMeta, abstractmethod
from ..benchmark import get_instances, get_length_by_token
from ..utils import draw_polygon, fit_image_in_box, get_overlap_area,\
    get_rectangular_area


class PipelineBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, tracker_constructor, verbose=False):
        self.tracker_constructor = tracker_constructor
        self.verbose = verbose

    @abstractmethod
    def run(self, data_provider=None, display_screen=(600, 800)):
        """given data, run the whole procedure
        @return: evaluation
        """
        pass

    @abstractmethod
    def eval(self, pred_results, gt_results):
        """eval given prediction and ground truth
        """
        pass


class NormalPipeline(PipelineBase):
    def run(self, data_provider=None, display_screen=None):
        if data_provider is None:
            data_provider = get_instances()
        eval_results = []
        for token, data_stream in get_instances():
            if self.verbose:
                print token
            instance_length = get_length_by_token(token)
            pbar = self.get_progressbar(instance_length) if self.verbose else\
                lambda x: x
            pred_results, gt_results = [], []
            for idx, (img, gt_coords) in pbar(enumerate(data_stream)):
                if display_screen is not None:
                    img = fit_image_in_box(img, display_screen)
                if idx == 0:
                    tracker = self.tracker_constructor(img, gt_coords)
                else:
                    pred_coords = tracker.track(img)
                    pred_results.append(pred_coords)
                    gt_results.append(gt_coords)
                    if not self.plot_stats(
                            img.copy(),
                            pred_coords, gt_coords, tracker,
                    ):
                        break  # user interception
            eval_results.append(self.eval(pred_results, gt_results))
            if self.verbose:
                print "\nevaluate: %.4f" % eval_results[-1]
        return eval_results

    def eval(self, pred_results, gt_results):
        overlap_areas = [get_overlap_area(p, g)
                         for p, g in zip(pred_results, gt_results)]
        normalized_areas = [
            float(area) / get_rectangular_area(gt_coords[0], gt_coords[2])
            for area, gt_coords in zip(overlap_areas, gt_results)
        ]
        X = np.linspace(0., 1., 100)  # 100 slices
        Y = np.array([sum([
            int(area >= threshold) for area in normalized_areas
        ]) / float(len(normalized_areas)) for threshold in X])
        return Y  # TODO
        #import matplotlib.pyplot as plt
        #plt.plot(X, Y)
        #plt.show()

    def get_progressbar(self, maxval):
        widgets = [progressbar.Percentage(), " ", progressbar.Bar(), " ",
                   progressbar.Counter(format="%d" + "/%d" % maxval)]
        pbar = progressbar.ProgressBar(maxval=maxval, widgets=widgets)
        return pbar

    def plot_stats(self, img, pred_coords, gt_coords, tracker):
        # plot particles distribution
        board = (np.zeros(img.shape) + 255).astype('uint8')
        for particle in sorted(
                tracker.particles, key=lambda x: x.weight,
        ):
            po = particle.center()
            po = (int(po[0] * board.shape[1]),
                  int(po[1] * board.shape[0]))
            cv2.circle(board, po, 1, (255, 0, 0), 1)
        # plot tracking results
        ## particle nearest to ground truth
        #particle = min(tracker.particles,
                       #key=lambda o: (o.coords[0][0] - gt_coords[0][0]) ** 2 + (o.coords[0][1] - gt_coords[0][1]) ** 2
                       #).copy()
        #draw_polygon(img, particle.coords, color=(0, 255, 255))
        draw_polygon(img, gt_coords, color=(0, 255, 0))
        draw_polygon(img, pred_coords, color=(0, 0, 255))
        if self.verbose:
            cv2.imshow('particles', board)
            cv2.imshow('img', img)
            #if idx == 1:
                #cv2.moveWindow("img", 0, 0)
                #cv2.moveWindow("particles", img.shape[1], 0)
            keyboard = chr(cv2.waitKey(0) & 0xFF)
            if keyboard == 'q':
                exit()
            elif keyboard == 's':  # skip token
                return False
        return True
