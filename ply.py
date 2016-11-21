#!/usr/bin/env python3

from model import ModelParser, Exporter, Vertex, Face

class PLYParser(ModelParser):

    def __init__(self):
        super().__init__()
        self.counter = 0
        self.elements = []
        self.inner_parser = PLYHeaderParser(self)

    def parse_line(self, string):
        self.inner_parser.parse_line(self, string)

class PLYHeaderParser:
    def __init__(self, parent):
        self.current_element = None
        self.parent = parent

    def parse_line(self, string):
        split = string.split(' ')
        if string == 'ply':
            return

        elif split[0] == 'format':
            if split[1] != 'ascii' or split[2] != '1.0':
                print('Only ascii 1.0 format is supported', file=sys.stderr)
                sys.exit(-1)

        elif split[0] == 'element':
            self.current_element = PLYElement(split[1], int(split[2]))
            self.parent.elements.append(self.current_element)

        elif split[0] == 'property':
            self.current_element.add_property(split[2], split[1])

        elif split[0] == 'end_header':
            self.parent.inner_parser = PLYContentParser(self.parent)


class PLYElement:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.properties = []

    def add_property(name, type):
        self.properties.append((name, type))

class PLYContentParser:
    def __init__(self, parent):
        self.parent = parent
        self.element_index = 0
        self.counter = 0
        self.current_element = self.parent.elements[0]

    def parse_line(self, string):
        self.counter += 1

        split = string.split(' ')

        if self.current_element.name == 'vertex':
            self.parent.add_vertex(Vertex.from_array(split))
        elif self.current_element.name == 'face':
            self.parent.add_face(Face(split[1], split[2], split[3]))

        self.counter += 1

    def next_element(self):
        self.element_index += 1
        self.current_element = self.parent.elements[self.element_index]

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


