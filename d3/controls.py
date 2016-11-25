#!/usr/bin/env python3

from .geometry import Vector

import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

import math

class Controls:
    def __init__(self):
        pass

    def apply(self):
        pass

    def update(self, time = 10):
        pass

class TrackBallControls(Controls):
    def __init__(self):
        super().__init__()
        self.vertex = Vector()
        self.theta = 0

    def apply(self):
        glRotatef(self.theta * 180 / math.pi, self.vertex.x, self.vertex.y, self.vertex.z)

    def update(self, time = 10):

        if not pygame.mouse.get_pressed()[0]:
            return

        coeff = 0.001
        move = pygame.mouse.get_rel()

        dV = Vector(move[1] * time * coeff, move[0] * time * coeff, 0)
        dTheta = dV.norm2()

        if abs(dTheta) < 0.00001:
            return

        dV.normalize()

        cosT2 = math.cos(self.theta / 2)
        sinT2 = math.sin(self.theta / 2)
        cosDT2 = math.cos(dTheta / 2)
        sinDT2 = math.sin(dTheta / 2)

        A = cosT2 * sinDT2 * dV + cosDT2 * sinT2 * self.vertex + sinDT2 * sinT2 * Vector.cross_product(dV, self.vertex)

        self.theta = 2 * math.acos(cosT2 * cosDT2 - sinT2 * sinDT2 * Vector.dot(dV, self.vertex))

        self.vertex = A
        self.vertex.normalize()

class OrbitControls(Controls):
    def __init__(self):
        super().__init__()
        self.phi = 0
        self.theta = 0

