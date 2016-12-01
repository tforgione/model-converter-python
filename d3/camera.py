from .geometry import Vector

from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    def __init__(self, position = None, target = None, up = None):
        self.position = Vector() if position is None else position
        self.target = Vector() if target is None else target
        self.up = Vector(0.0,1.0,0.0) if up is None else target

    def look(self):
        gluLookAt(
            self.position.x, self.position.y, self.position.z,
            self.target.x, self.target.y, self.target.z,
            self.up.x, self.up.y, self.up.z)
