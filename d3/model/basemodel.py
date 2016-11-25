#!/usr/bin/env python3

from math import sqrt

from ..geometry import Vector

Vertex = Vector
Normal = Vertex
TexCoord = Vertex

class FaceVertex:
    def __init__(self, vertex = None, texture = None, normal = None):
        self.vertex = vertex
        self.texture = texture
        self.normal = normal

    def from_array(self, arr):
        self.vertex  = int(arr[0]) if len(arr) > 0 else None

        try:
            self.texture = int(arr[1]) if len(arr) > 1 else None
        except:
            self.texture = None

        try:
            self.normal  = int(arr[2]) if len(arr) > 2 else None
        except:
            self.normal = None

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
        self.vertex_vbo = None
        self.tex_coord_vbo = None
        self.normal_vbo = None

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

    def draw(self):

        import OpenGL.GL as gl

        gl.glColor3f(1.0,0.0,0.0)

        if self.center_and_scale:
            center = self.bounding_box.get_center()
            scale = self.bounding_box.get_scale() / 2
            gl.glPushMatrix()
            gl.glScalef(1/scale, 1/scale, 1/scale)
            gl.glTranslatef(-center.x, -center.y, -center.z)

        if self.vertex_vbo is not None:

            self.vertex_vbo.bind()
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY);
            gl.glVertexPointerf(self.vertex_vbo)
            self.vertex_vbo.unbind()

            self.normal_vbo.bind()
            gl.glEnableClientState(gl.GL_NORMAL_ARRAY);
            gl.glNormalPointerf(self.normal_vbo)
            self.normal_vbo.unbind()

            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.vertex_vbo.data) * 9)

        else:

            gl.glBegin(gl.GL_TRIANGLES)
            for face in self.faces:
                v1 = self.vertices[face.a.vertex]
                v2 = self.vertices[face.b.vertex]
                v3 = self.vertices[face.c.vertex]

                if face.a.normal is not None:
                    n1 = self.normals[face.a.normal]
                    n2 = self.normals[face.b.normal]
                    n3 = self.normals[face.c.normal]

                if face.a.normal is not None:
                    gl.glNormal3f(n1.x, n1.y, n1.z)
                gl.glVertex3f(v1.x, v1.y, v1.z)

                if face.b.normal is not None:
                    gl.glNormal3f(n2.x, n2.y, n2.z)
                gl.glVertex3f(v2.x, v2.y, v2.z)

                if face.c.normal is not None:
                    gl.glNormal3f(n3.x, n3.y, n3.z)
                gl.glVertex3f(v3.x, v3.y, v3.z)

            gl.glEnd()

        if self.center_and_scale:
            gl.glPopMatrix()

    def generate_vbos(self):
        from OpenGL.arrays import vbo
        from numpy import array
        # Build VBO
        v = []
        n = []

        for face in self.faces:
            v1 = self.vertices[face.a.vertex]
            v2 = self.vertices[face.b.vertex]
            v3 = self.vertices[face.c.vertex]
            v += [[v1.x, v1.y, v1.z], [v2.x, v2.y, v2.z], [v3.x, v3.y, v3.z]]

            if face.a.normal is not None:
                n1 = self.normals[face.a.normal]
                n2 = self.normals[face.b.normal]
                n3 = self.normals[face.c.normal]
                n += [[n1.x, n1.y, n1.z], [n2.x, n2.y, n2.z], [n3.x, n3.y, n3.z]]

        self.vertex_vbo = vbo.VBO(array(v, 'f'))
        self.normal_vbo = vbo.VBO(array(n, 'f'))

    def generate_vertex_normals(self):
        self.normals = [Normal() for i in self.vertices]

        for face in self.faces:
            v1 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.b.vertex])
            v2 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.c.vertex])
            cross = Vertex.cross_product(v1, v2)
            self.normals[face.a.vertex] += cross
            self.normals[face.b.vertex] += cross
            self.normals[face.c.vertex] += cross

        for normal in self.normals:
            normal.normalize()

        for face in self.faces:
            face.a.normal = face.a.vertex
            face.b.normal = face.b.vertex
            face.c.normal = face.c.vertex

    def generate_face_normals(self):

        self.normals = [Normal() for i in self.faces]

        for (index, face) in enumerate(self.faces):

            v1 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.b.vertex])
            v2 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.c.vertex])
            cross = Vertex.cross_product(v1, v2)
            cross.normalize()
            self.normals[index] = cross

            face.a.normal = index
            face.b.normal = index
            face.c.normal = index


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


