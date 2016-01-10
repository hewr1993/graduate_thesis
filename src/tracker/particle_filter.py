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
    def __init__(self, coords, weight=1.,
                 _width=40, _height=40):
        """
        @type coords: [(w, h), ...] for 4 corners (relative coordinates)
        @param _width, _height: builtin image patch size
        """
        self.coords = coords
        self.weight = weight
        self._patch_shape = (_height, _width)

    def copy(self):
        return Particle(self.coords, self.weight,
                        self._patch_shape[1], self._patch_shape[0])

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, value):
        self._coords = [(x, y) for x, y in value]  # deep copy

    def add_noise(self, level=0.1):
        # FIXME: box in boundary
        ox, oy = noise(level), noise(level)
        self.coords = [(x + ox, y + oy) for x, y in self.coords]
        coords = []
        for x, y in self.coords:
            x = max(min(x + ox, 1.), 0.)
            y = max(min(y + oy, 1.), 0.)
            coords.append((x, y))
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
    def __init__(self, first_frame, bounding_box, nr_particle=1000):
        """
        @param nr_particle: number of particles
        @type bounding_box: [(w, h), ...] for 4 corners
        """
        self.bounding_box = ensure_relative_coordinates(bounding_box,
                                                        first_frame.shape[:2])
        self.object_template = Particle(bounding_box)\
            .patch_given_image(first_frame)
        self.particles = [Particle(bounding_box) for _ in xrange(nr_particle)]
        for particle in self.particles:
            particle.add_noise()

    def resample(self):
        rng = np.random.RandomState()
        norm_weights = normalize([p.weight for p in self.particles])
        dist = rng.choice(len(self.particles), len(self.particles),
                          p=norm_weights)
        particles = []
        for idx in dist:
            p = self.particles[idx].copy()
            p.add_noise()
            particles.append(p)
        self.particles = particles

    def evaluate(self, frame):
        for particle in self.particles:
            patch_img = particle.patch_given_image(frame)
            particle.weight = histogram_similarity(
                self.object_template, patch_img,
                method=cv.CV_COMP_BHATTACHARYYA,
                normalize=False,
            )
        return max(self.particles, key=lambda x: x.weight).copy()

    def track(self, frame):
        ans_particle = self.evaluate(frame)
        self.resample()
        return ans_particle.coords