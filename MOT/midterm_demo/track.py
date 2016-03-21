#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Mar 20 18:44:42 2016
# Mail: hewr2010@gmail.com
import sys
import cv2
import math
import numpy as np
from detect import *
from sklearn.utils.linear_assignment_ import linear_assignment
from filterpy.kalman import KalmanFilter


def xywh_to_xysr(x, y, w, h):
    return (x, y, float(w) * h, float(w) / h)


def xysr_to_xywh(x, y, s, r):
    return (x, y, math.sqrt(s * r), math.sqrt(s / r))


def iou(l, r):
    """
    @param l, r: in form of (x, y, w, h)
    """
    x0, y0 = max(l[0], r[0]), max(l[1], r[1])
    x1, y1 = min(l[0] + l[2], r[0] + r[2]), min(l[1] + l[3], r[1] + r[3])
    area = max(0, x1 - x0) * max(0, y1 - y0)
    s0, s1 = l[2] * l[3], r[2] * r[3]
    ratio = area / float(s0 + s1 - area)
    return ratio


class Tracker(object):
    count = 0

    def __init__(self, birth, det, MAX_ABSENCE=2, MIN_HITS=3):
        """
        @param birth: in which frame it was created
        @param det: detection (x, y, w, h)
        @param MAX_ABSENCE: keep an object within MAX_ABSENCE \
            consecutive missing frames
        @param MIN_HITS: confirm an object after MIN_HITS \
            consecutive detected frames
        """
        self.id = 0
        self.birth = birth
        self.last_hit = birth
        self.model = self.create_kalman_filter(det)
        self.MAX_ABSENCE = MAX_ABSENCE
        self.MIN_HITS = MIN_HITS
        self.confirmed = False  # once confirmed as an object, it's forever

    def create_kalman_filter(self, det):
        """(x, y, s(area), r(aspect ratio), x', y', s')
        """
        model = KalmanFilter(dim_x=7, dim_z=4)
        model.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ], 'float32')
        model.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ], 'float32')
        model.R[2:,2:] *= 10.
        model.P[4:,4:] *= 1000.  # high uncertainty of initial volocity
        model.P *= 10.
        model.Q[-1,-1] *= 0.01
        model.Q[4:,4:] *= 0.01
        model.x[:4] = np.array(xywh_to_xysr(*det), 'float32').reshape(4, 1)
        return model

    def bounding_box(self):
        return xysr_to_xywh(*(self.model.x[:4].reshape(-1)))

    def update(self, age, det):
        """match a detection bounding box at frame age
        """
        self.last_hit = age
        if not self.confirmed:
            if age - self.birth + 1 >= self.MIN_HITS:
                self.confirmed = True
                Tracker.count += 1
                self.id = Tracker.count
        self.model.update(np.array(xywh_to_xysr(*det), 'float32').reshape(4, 1))
        if self.model.x[6] + self.model.x[2] <= 0.:  # FIXME necessary?
            self.model.x[6] = 0.
        self.model.predict()

    def alive(self, age):
        """whether it's dead at age, not necessary to be activated
        """
        if not self.confirmed:
            return self.last_hit == age
        else:
            return age - self.last_hit <= self.MAX_ABSENCE

    def active(self, age):
        """whether it's activated at age
        """
        if not self.confirmed:
            return age <= self.MIN_HITS
        else:
            return self.last_hit == age


class Monitor(object):
    def __init__(self, tracker_constructor,
                 DETECT_THRESHOLD=0.3, IOU_THRESHOLD=0.3):
        """
        @param tracker_constructor: used to create new tracker \
            tracker_constructor(birth, det)
        @param IOU_THRESHOLD: used in detections matching
        """
        self.age = 0  # how many passed frames
        self.tracker_constructor = tracker_constructor
        self.DETECT_THRESHOLD = DETECT_THRESHOLD
        self.IOU_THRESHOLD = IOU_THRESHOLD
        self.trackers = []  # tracked objects

    def get_detections(self):
        """current position (x, y, w, h) of instances
        """
        return [trk.bounding_box() for trk in self.trackers]

    def match_detections(self, old_dets, new_dets, iou_threshold):
        if len(old_dets) == 0 or len(new_dets) == 0:
            return []
        iou_cost = np.array(
            [[iou(old, new) for new in new_dets] for old in old_dets],
            'float32'
        )
        match_pairs = linear_assignment(-iou_cost)
        return match_pairs

    def maintain_trackers(self, dets):
        old_dets = self.get_detections()
        match_pairs = self.match_detections(old_dets, dets, self.IOU_THRESHOLD)
        # update matching trackers
        for old_idx, new_idx in match_pairs:
            self.trackers[old_idx].update(self.age, dets[new_idx])
        # update missing trackers
        self.trackers = [trk for trk in self.trackers if trk.alive(self.age)]
        # create new trackers
        for i in list(
                set(range(len(dets))).difference(set([r for l, r in match_pairs]))
        ):
            self.trackers.append(self.tracker_constructor(self.age, dets[i]))

    def monitor(self, frame):
        """
        @return: [(x, y, w, h, id)]
        """
        self.age += 1
        # calculate heatmap
        # FIXME assume it's heatmap of detections
        heatmap = frame
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        heatmap = cv2.dilate(heatmap, kernel)
        heatmap = cv2.erode(heatmap, kernel)
        heatmap[heatmap <= self.DETECT_THRESHOLD] = 0
        # calculate detections (x, y, w, h)
        dets = get_detections(heatmap)
        dets = [bbox for bbox, _, _ in dets]
        # track detections
        self.maintain_trackers(dets)
        ret = [
            map(int, trk.bounding_box() + (trk.id if trk.id > 0 else i + 1,))
            for i, trk in enumerate(self.trackers) if trk.active(self.age)
        ]
        return ret


def get_progressbar(maxval):
    import progressbar as pb
    widgets = [pb.Percentage(), " ", pb.Bar(), " ",
               pb.Counter(format="%d" + "/%d" % maxval),
               " [", pb.ETA(), "]"]
    pbar = pb.ProgressBar(maxval=maxval, widgets=widgets)
    return pbar

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="image_expr", nargs="+")
    parser.add_argument("--max_height", type=int, default=540)
    parser.add_argument("--max_width", type=int, default=960)
    parser.add_argument("--max_absence", type=int, default=5)
    parser.add_argument("--min_hits", type=int, default=3)
    parser.add_argument("--detect_threshold", type=float, default=0)
    parser.add_argument("--iou_threshold", type=float, default=0.3)
    parser.add_argument("--delay", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # initialize
    tracker_constructor = lambda birth, det: Tracker(
        birth, det,
        MAX_ABSENCE=args.max_absence,
        MIN_HITS=args.min_hits,
    )
    monitor = Monitor(tracker_constructor,
                      DETECT_THRESHOLD=args.detect_threshold,
                      IOU_THRESHOLD=args.iou_threshold)
    colors = []
    # main process
    paths = parse_paths(args.image_expr)
    for frame_cnt, (origin_path, heatmap_path) in \
            get_progressbar(len(paths))(enumerate(paths)):
        # heatmap related
        ori_img = get_in_box(cv2.imread(origin_path), (args.max_height, args.max_width))
        heatmap = get_in_box(cv2.imread(heatmap_path), (args.max_height, args.max_width))
        # predict
        tracking_results = monitor.monitor(heatmap)
        # display
        if args.verbose:
            img = heatmap.copy()
            for (x, y, w, h), bbox, approx in get_detections(heatmap):
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.drawContours(img, np.array([cv2.cv.BoxPoints(bbox)], 'int64'), 0, (0, 0, 255), 1)
                cv2.polylines(img, np.array([approx], 'int64'), True, (255, 0, 0), 1)
            cv2.imshow("information", img)
        img = ori_img.copy()
        for x, y, w, h, _id in tracking_results:
            # prepare color
            while len(colors) < _id:
                colors.append(tuple(np.random.randint(0, 255, 3)))
            cv2.rectangle(img, (x, y), (x + w, y + h), colors[_id - 1], 2)
            cv2.putText(img, str(_id), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255)
        cv2.imshow('result', img)
        if chr(cv2.waitKey(args.delay) & 0xFF) == 'q':
            exit()
