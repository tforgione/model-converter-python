#!/usr/bin/env python3

import sys
from functools import reduce

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

    def addFace(self, face):
        self.faces.append(face)

    def parse_line(self, string):
        pass

    def parse_file(self, path):
        with open(path) as f:
            for line in f.readlines():
                line = line.rstrip()
                self.parse_line(line)

class OBJParser(ModelParser):

    def __init__(self):
        super().__init__()
        self.materials = []

    def parse_line(self, string):
        split = string.split(' ')
        first = split[0]
        split = split[1:]

        if first == 'usemtl':
            self.currentMaterial = split[0]
        elif first == 'v':
            self.add_vertex(Vertex().from_array(split))
        elif first == 'vn':
            self.add_normal(Normal().from_array(split))
        elif first == 'vt':
            self.add_tex_coord(TexCoord().from_array(split))
        elif first == 'f':
            splits = list(map(lambda x: x.split('/'), split))

            for i in range(len(splits)):
                for j in range(len(splits[i])):
                    splits[i][j] = str(int(splits[i][j]) - 1)

            self.addFace(Face().from_array(splits))

class Exporter:
    def __init__(self, model):
        self.model = model

class OBJExporter(Exporter):
    def __init__(self, model):
        super().__init__(model)

    def __str__(self):
        string = ""

        for vertex in self.model.vertices:
            string += "n " + ' '.join([vertex.x, vertex.y, vertex.z]) + "\n"

        string += "\n"

        for tex_coord in self.model.tex_coords:
            string += "vt " + ' '.join([tex_coord.x, tex_coord.y]) + "\n"

        string += "\n"

        for normal in self.model.normals:
            string += "vn " + ' '.join([normal.x, normal.y, normal.z]) + "\n"

        string += "\n"

        for face in self.model.faces:
            string += "f "
            arr = []
            for v in [face.a, face.b, face.c]:
                sub_arr = []
                sub_arr.append(v.vertex)
                if v.normal is None:
                    if v.texture is not None:
                        sub_arr.append('')
                        sub_arr.append(v.texture)
                elif v.texture is not None:
                    sub_arr.append(v.texture)
                    if v.normal is not None:
                        sub_arr.append(v.normal)
                arr.append('/'.join(sub_arr))

            string += ' '.join(arr) + '\n'
        return string

class PLYExporter(Exporter):
    def __init__(self, model):
        super().__init__(model)

    def __str__(self):
        # Header
        string = "ply\nformat ascii 1.0\ncomment Automatically gnerated by model-converter\n"

        # Types : vertices
        string += "element vertex " + str(len(self.model.vertices)) +"\n"
        string += "property float32 x\nproperty float32 y\nproperty float32 z\n"

        # Types : faces
        string += "element face " + str(len(self.model.faces)) + "\n"
        string += "property list uint8 int32 vertex_indices\n"

        # End header
        string += "end_header\n"

        # Content of the model
        for vertex in self.model.vertices:
            string += vertex.x + " " + vertex.y + " " + vertex.z + "\n"

        for face in self.model.faces:
            string += "3 " + face.a.vertex + " " + face.b.vertex + " " + face.c.vertex + "\n"

        return string

if __name__ == '__main__':

    parser = OBJParser()
    parser.parse_file('./examples/cube.obj')

    exporter = PLYExporter(parser)
    string = str(exporter)

    print(string)


