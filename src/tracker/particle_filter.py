#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 02:07:24 2016
# Purpose: particle filter object tracker
# Mail: hewr2010@gmail.com
import cv
import cv2
import numpy as np
from base import Tracker
from ..utils import ensure_relative_coordinates, ensure_absolute_coordinates,\
    noise, histogram_similarity, normalize


class Particle(object):
    def __init__(self, coords,
                 fixed_size=True, weight=1.,
                 _width=40, _height=40):
        """
        @param coords: should be parallelogram
        @type coords: [(w, h), ...] for 4 corners (relative coordinates)
        @param _width, _height: patch image size
        """
        self.coords = coords
        self.fixed_size = fixed_size
        self.weight = weight
        self._patch_shape = (_height, _width)

    def copy(self):
        return Particle(self.coords, self.fixed_size, self.weight,
                        self._patch_shape[1], self._patch_shape[0])

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, value):
        self._coords = [(x, y) for x, y in value]  # deep copy

    def center(self):
        xs, ys = zip(*self.coords)
        x = sum(xs) / len(xs)
        y = sum(ys) / len(ys)
        return (x, y)

    # FIXME faster implement
    def add_noise(self, level=0.1):
        def in_boundary(coords):
            for x, y in coords:
                if x < 0. or x > 1. or y < 0. or y > 1.:
                    return False
            return True

        while True:
            ox, oy = noise(level), noise(level)
            coords = [(x + ox, y + oy) for x, y in self.coords]
            if not self.fixed_size:
                ol = noise(level, 1.)
                o = np.array(coords[0])
                vx = (np.array(coords[1]) - o) * ol
                vy = (np.array(coords[-1]) - o) * ol
                coords = map(tuple, [o, o + vx, o + vx + vy, o + vy])
            if in_boundary(coords):
                break
        self.coords = coords

    def patch_given_image(self, img):
        # TODO homography
        coords = ensure_absolute_coordinates(self.coords, img.shape[:2])
        coords = [[x, y] for x, y in coords]  # for changable object
        if coords[0][1] == coords[-2][1]:
            if coords[0][1] == 0:
                coords[-2][1] += 1
            else:
                coords[0][1] -= 1
        if coords[0][0] == coords[-2][0]:
            if coords[0][0] == 0:
                coords[-2][0] += 1
            else:
                coords[0][0] -= 1
        patch_img = img[coords[0][1]:coords[-2][1],
                        coords[0][0]:coords[-2][0]].copy()
        try:
            return cv2.resize(patch_img, self._patch_shape[::-1])
        except:
            from IPython import embed; embed()
            exit()


class ParticleFilterTracker(Tracker):
    def __init__(self, first_frame, bounding_box, nr_particle=1000,
                 fixed_size=True):
        """
        @param nr_particle: number of particles
        @type bounding_box: [(w, h), ...] for 4 corners
        """
        self.bounding_box = ensure_relative_coordinates(bounding_box,
                                                        first_frame.shape[:2])
        self.object_template = Particle(bounding_box)\
            .patch_given_image(first_frame)
        self.fixed_size = fixed_size
        self.particles = [Particle(bounding_box, fixed_size=self.fixed_size)
                          for _ in xrange(nr_particle)]
        for particle in self.particles:
            particle.add_noise(level=0.1)

    def resample(self):
        rng = np.random.RandomState()
        norm_weights = normalize([p.weight for p in self.particles])
        dist = rng.choice(len(self.particles), len(self.particles),
                          p=norm_weights)
        particles = []
        for idx in dist:
            p = self.particles[idx].copy()
            p.add_noise(level=0.05)
            particles.append(p)
        self.particles = particles

    def evaluate(self, frame):
        """evaluate particles given current frame
        """
        return max(self.particles, key=lambda x: x.weight).copy()

    def track(self, frame):
        ans_particle = self.evaluate(frame)
        self.resample()
        return ans_particle.coords


class HistogramParticleFilterTracker(ParticleFilterTracker):
    def evaluate(self, frame):
        for particle in self.particles:
            patch_img = particle.patch_given_image(frame)
            particle.weight = 1 - histogram_similarity(
                self.object_template, patch_img,
                method=cv.CV_COMP_BHATTACHARYYA,
                normalize=True,
            )
        return super(HistogramParticleFilterTracker, self).evaluate(frame)
