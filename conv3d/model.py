#!/usr/bin/env python3

class Vertex:
    def __init__(self, x = None, y = None, z = None):
        self.x = x
        self.y = y
        self.z = z

    def from_array(self, arr):
        self.x = float(arr[0]) if len(arr) > 0 else None
        self.y = float(arr[1]) if len(arr) > 1 else None
        self.z = float(arr[2]) if len(arr) > 2 else None
        return self

Normal = Vertex
TexCoord = Vertex

class FaceVertex:
    def __init__(self, vertex = None, texture = None, normal = None):
        self.vertex = vertex
        self.texture = texture
        self.normal = normal

    def from_array(self, arr):
        self.vertex  = int(arr[0]) if len(arr) > 0 else None
        self.texture = int(arr[1]) if len(arr) > 1 else None
        self.normal  = int(arr[2]) if len(arr) > 2 else None
        return self

class Face:
    def __init__(self, a = None, b = None, c = None, mtl = None):
        self.a = a
        self.b = b
        self.c = c
        self.mtl = mtl

    # Expects array of array
    def from_array(self, arr):
        self.a = FaceVertex().from_array(arr[0])
        self.b = FaceVertex().from_array(arr[1])
        self.c = FaceVertex().from_array(arr[2])
        return self

class ModelParser:

    def __init__(self):
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.faces = []
        self.bounding_box = BoundingBox()
        self.center_and_scale = True

    def add_vertex(self, vertex):
        self.vertices.append(vertex)
        self.bounding_box.add(vertex)

    def add_tex_coord(self, tex_coord):
        self.tex_coords.append(tex_coord)

    def add_normal(self, normal):
        self.normals.append(normal)

    def add_face(self, face):
        self.faces.append(face)

    def parse_line(self, string):
        pass

    def parse_file(self, path):
        with open(path) as f:
            for line in f.readlines():
                line = line.rstrip()
                self.parse_line(line)

    def gl_draw(self):

        import OpenGL.GL as gl

        gl.glColor3f(1.0,0.0,0.0)

        if self.center_and_scale:
            center = self.bounding_box.get_center()
            scale = self.bounding_box.get_scale() / 2
            gl.glPushMatrix()
            gl.glScalef(1/scale, 1/scale, 1/scale)
            gl.glTranslatef(-center.x, -center.y, -center.z)

        gl.glBegin(gl.GL_TRIANGLES)
        for face in self.faces:
            v1 = self.vertices[face.a.vertex]
            v2 = self.vertices[face.b.vertex]
            v3 = self.vertices[face.c.vertex]
            gl.glVertex3f(v1.x, v1.y, v1.z)
            gl.glVertex3f(v2.x, v2.y, v2.z)
            gl.glVertex3f(v3.x, v3.y, v3.z)
        gl.glEnd()

        if self.center_and_scale:
            gl.glPopMatrix()

class BoundingBox:
    def __init__(self):
        self.min_x = +float('inf')
        self.min_y = +float('inf')
        self.min_z = +float('inf')

        self.max_x = -float('inf')
        self.max_y = -float('inf')
        self.max_z = -float('inf')

    def add(self, vertex):
        self.min_x = min(self.min_x, vertex.x)
        self.min_y = min(self.min_y, vertex.y)
        self.min_z = min(self.min_z, vertex.z)

        self.max_x = max(self.max_x, vertex.x)
        self.max_y = max(self.max_y, vertex.y)
        self.max_z = max(self.max_z, vertex.z)

    def __str__(self):
        return "[{},{}],[{},{}],[{},{}]".format(
            self.min_x,
            self.min_y,
            self.min_z,
            self.max_x,
            self.max_y,
            self.max_z)

    def get_center(self):
        return Vertex(
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2)

    def get_scale(self):
        return max(
            abs(self.max_x - self.min_x),
            abs(self.max_y - self.min_y),
            abs(self.max_z - self.min_z))


class Exporter:
    def __init__(self, model):
        self.model = model


