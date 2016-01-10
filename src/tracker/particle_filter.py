#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sun Jan 10 02:07:24 2016
# Purpose: particle filter object tracker
# Mail: hewr2010@gmail.com
from base import Tracker
from ..utils import ensure_relative_coordinates, noise


class Particle(object):
    def __init__(self, coords, weight=0,
                 _width=40, _height=40):
        """
        @type coords: [(w, h), ...] for 4 corners
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
        ox, oy = noise(level), noise(level)
        self.coords = [(x + ox, y + oy) for x, y in self.coords]

    def patch_given_image(self, img):
        # TODO homography
        return img[self.coords[0][1]:self.coords[-1][1],
                   self.coords[0][0]:self.coords[-1][0]].copy()


class ParticleFilterTracker(Tracker):
    def __init__(self, first_frame, bounding_box, nr_particle=10):
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
        # TODO
        pass

    def evaluate(self, frame):
        # TODO
        for particle in self.particles:
            particle.weight += noise(0.1)  # TODO delete
        self.particles.sort(key=lambda x: x.weight, reverse=True)

    def track(self, frame):
        self.evaluate(frame)
        ans_particle = self.particles[0].copy()
        self.resample()
        return ans_particle.coords
