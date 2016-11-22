#!/usr/bin/env python3

class Vertex:
    def __init__(self, x = None, y = None, z = None):
        self.x = x
        self.y = y
        self.z = z

    def from_array(self, arr):
        self.x = arr[0] if len(arr) > 0 else None
        self.y = arr[1] if len(arr) > 1 else None
        self.z = arr[2] if len(arr) > 2 else None
        return self

Normal = Vertex
TexCoord = Vertex

class FaceVertex:
    def __init__(self, vertex = None, texture = None, normal = None):
        self.vertex = vertex
        self.texture = texture
        self.normal = normal

    def from_array(self, arr):
        self.vertex  = arr[0] if len(arr) > 0 else None
        self.texture = arr[1] if len(arr) > 1 else None
        self.normal  = arr[2] if len(arr) > 2 else None
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

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

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

class Exporter:
    def __init__(self, model):
        self.model = model


