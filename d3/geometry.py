#!/usr/bin/env python3

import math

class Vector:
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def from_array(self, arr):
        self.x = float(arr[0]) if len(arr) > 0 else None
        self.y = float(arr[1]) if len(arr) > 1 else None
        self.z = float(arr[2]) if len(arr) > 2 else None
        return self

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def norm2(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def norm(self):
        return math.sqrt(self.norm2())

    def normalize(self):
        norm = self.norm()
        if abs(norm) > 0.0001:
            self.x /= norm
            self.y /= norm
            self.z /= norm

    def cross_product(v1, v2):
        return Vector(
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x)

    def from_points(v1, v2):
        return Vector(
            v2.x - v1.x,
            v2.y - v1.y,
            v2.z - v1.z)

    def __str__(self):
        return '(' + ", ".join([str(self.x), str(self.y), str(self.z)]) + ")"

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z


