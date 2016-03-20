#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Mar 20 00:19:19 2016
# Mail: hewr2010@gmail.com
import os
import cv2
import glob
import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(dest="image_expr", nargs="+")
parser.add_argument("--max_height", type=int, default=540)
parser.add_argument("--max_width", type=int, default=960)
args = parser.parse_args()


def parse_paths(paths):
    paths = [path for path in args.image_expr if path[-12:-4] != "_heatmap"]
    paths.sort(key=lambda s: (os.path.dirname(s), int(os.path.splitext(os.path.basename(s))[0])))
    paths = [(path, path[:-4] + "_heatmap" + path[-4:]) for path in paths]
    return paths


def get_in_box(img, max_shape):
    r_h = float(img.shape[0]) / max_shape[0]
    r_w = float(img.shape[1]) / max_shape[1]
    r = max(r_h, r_w)
    shape = (int(img.shape[0] / r), int(img.shape[1] / r))
    return cv2.resize(img, shape[::-1], interpolation=cv2.INTER_AREA)


#def xywh_to_coords(x, y, w, h):
    #return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def is_negative(mask, rect, threshold=0.7):
    w, h = rect[2] / 4, rect[3] / 4
    a = mask[rect[1] + h:rect[1] + h * 3, rect[0] + w:rect[0] + w * 3]
    x = (a > 0).astype('int64').sum()
    ratio = float(x) / (w * h * 4) if w * h > 0 else 1.
    return ratio < threshold


def get_detections(heatmap):
    boxes = []
    mask = heatmap[:, :, 0].copy().astype("uint8")
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area = cv2.contourArea(c)
        if area / float(mask.shape[0] * mask.shape[1]) < 0.02:
            continue
        rect = cv2.boundingRect(c)
        if is_negative(mask, rect):
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        boxes.append((cv2.boundingRect(c), cv2.minAreaRect(c), [tuple(p) for (p,) in approx]))
    return boxes

if __name__ == "__main__":
    paths = parse_paths(args.image_expr)
    for origin_path, heatmap_path in paths:
        print origin_path
        # heatmap related
        ori_img = get_in_box(cv2.imread(origin_path), (args.max_height, args.max_width))
        heatmap = get_in_box(cv2.imread(heatmap_path), (args.max_height, args.max_width))
        merged = (ori_img * np.maximum(0.2, heatmap / 255.)).astype("uint8")
        # detection results
        boxes = get_detections(heatmap.copy())
        for (x, y, w, h), bbox, approx in boxes:
            # heatmap
            cv2.rectangle(heatmap, (x, y), (x + w, y + h), (0, 255, 0), 1)
            cv2.drawContours(heatmap, np.array([cv2.cv.BoxPoints(bbox)], 'int64'), 0, (0, 0, 255), 1)
            cv2.polylines(heatmap, np.array([approx], 'int64'), True, (255, 0, 0), 1)
            # merged
            cv2.rectangle(merged, (x, y), (x + w, y + h), (0, 255, 0), 1)
            cv2.drawContours(merged, np.array([cv2.cv.BoxPoints(bbox)], 'int64'), 0, (0, 0, 255), 1)
            cv2.polylines(merged, np.array([approx], 'int64'), True, (255, 0, 0), 1)
            # origin image
            if len(approx) == 4 and False:  # False because of bad empirical result
                cv2.polylines(ori_img, np.array([approx], 'int64'), True, (0, 0, 255), 2)
            else:
                cv2.drawContours(ori_img, np.array([cv2.cv.BoxPoints(bbox)], 'int64'), 0, (0, 0, 255), 2)
        # display
        cv2.imshow("heatmap", heatmap)
        cv2.imshow("merged", merged)
        cv2.imshow("result", ori_img)
        if chr(cv2.waitKey(0) & 0xFF) == 'q':
            exit()
