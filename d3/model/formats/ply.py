import os
import sys
import PIL
import struct
from ..basemodel import ModelParser, TextModelParser, Exporter, Vertex, Face, FaceVertex, TexCoord, Material

class UnkownTypeError(Exception):
    def __init__(self, message):
        self.message  = message

def is_ply(filename):
    return filename[-4:] == '.ply'

# List won't work with this function
def _ply_type_size(type):
    if type == 'char' or type == 'uchar':
        return 1
    elif type == 'short' or type == 'ushort':
        return 2
    elif type == 'int' or type == 'uint':
        return 4
    elif type == 'float':
        return 4
    elif type == 'double':
        return 8
    else:
        raise UnkownTypeError('Type ' + type + ' is unknown')

def ply_type_size(type):
    split = type.split()

    if len(split) == 1:
        return [_ply_type_size(type)]
    else:
        if split[0] != 'list':
            print('You have multiple types but it\'s not a list...', file=sys.stderr)
            sys.exit(-1)
        else:
            return list(map(lambda a: _ply_type_size(a), split[1:]))


def bytes_to_element(type, bytes, byteorder = 'little'):
    if type == 'char':
        return ord(struct.unpack('<b', bytes)[0])
    if type == 'uchar':
        return ord(struct.unpack('<c', bytes)[0])
    elif type == 'short':
        return struct.unpack('<h', bytes)[0]
    elif type == 'ushort':
        return struct.unpack('<H', bytes)[0]
    elif type == 'int':
        return struct.unpack('<i', bytes)[0]
    elif type == 'uint':
        return struct.unpack('<I', bytes)[0]
    elif type == 'float':
        return struct.unpack('<f', bytes)[0]
    elif type == 'double':
        return struct.unpack('<d', bytes)[0]
    else:
        raise UnkownTypeError('Type ' + type + ' is unknown')

class PLYParser(ModelParser):

    def __init__(self, up_conversion = None):
        super().__init__(up_conversion)
        self.counter = 0
        self.elements = []
        self.materials = []
        self.inner_parser = PLYHeaderParser(self)
        self.beginning_of_line = ''
        self.header_finished = False

    def parse_bytes(self, bytes, byte_counter):
        if self.header_finished:
            self.inner_parser.parse_bytes(self.beginning_of_line + bytes, byte_counter - len(self.beginning_of_line))
            self.beginning_of_line = b''
            return

        # Build lines for header and use PLYHeaderParser
        current_line = self.beginning_of_line
        for (i, c) in enumerate(bytes):
            char = chr(c)
            if char == '\n':
                self.inner_parser.parse_line(current_line)
                if  current_line == 'end_header':
                    self.header_finished = True
                    self.beginning_of_line = bytes[i+1:]
                    return
                current_line = ''
            else:
                current_line += chr(c)
        self.beginning_of_line = current_line

class PLYHeaderParser:
    def __init__(self, parent):
        self.current_element = None
        self.parent = parent
        self.content_parser = None

    def parse_line(self, string):
        split = string.split()
        if string == 'ply':
            return

        elif split[0] == 'format':
            if split[2] != '1.0':
                print('Only format 1.0 is supported', file=sys.stderr)
                sys.exit(-1)

            if split[1] == 'ascii':
                self.content_parser = PLY_ASCII_ContentParser(self.parent)
            elif split[1] == 'binary_little_endian':
                self.content_parser = PLYLittleEndianContentParser(self.parent)
            elif split[1] == 'binary_big_endian':
                self.content_parser = PLYBigEndianContentParser(self.parent)
            else:
                print('Only ascii, binary_little_endian and binary_big_endian are supported', \
                      file=sys.stderr)
                sys.exit(-1)

        elif split[0] == 'element':
            self.current_element = PLYElement(split[1], int(split[2]))
            self.parent.elements.append(self.current_element)

        elif split[0] == 'property':
            self.current_element.add_property(split[-1], ' '.join(split[1:-1]))

        elif split[0] == 'end_header':
            self.parent.inner_parser = self.content_parser

        elif split[0] == 'comment' and split[1] == 'TextureFile':
            material = Material('mat' + str(len(self.parent.materials)))
            self.parent.materials.append(material)

            try:
                material.map_Kd = PIL.Image.open(os.path.join(os.path.dirname(self.parent.path), split[2]))
            except ImportError:
                pass

class PLYElement:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.properties = []

    def add_property(self, name, type):
        self.properties.append((name, type))

class PLY_ASCII_ContentParser:
    def __init__(self, parent):
        self.parent = parent
        self.element_index = 0
        self.counter = 0
        self.current_element = None
        self.beginning_of_line = ''

    def parse_bytes(self, bytes, byte_counter):
        current_line = self.beginning_of_line
        for (i, c) in enumerate(bytes):
            char = chr(c)
            if char == '\n':
                self.parse_line(current_line)
                current_line = ''
            else:
                current_line += chr(c)
        self.beginning_of_line = current_line


    def parse_line(self, string):

        if self.current_element is None:
            self.current_element = self.parent.elements[0]

        split = string.split()

        if self.current_element.name == 'vertex':
            self.parent.add_vertex(Vertex().from_array(split))
        elif self.current_element.name == 'face':

            faceVertexArray = []
            current_material = None

            # Analyse element
            offset = 0
            for property in self.current_element.properties:
                if property[0] == 'vertex_indices':
                    for i in range(int(split[offset])):
                        faceVertexArray.append(FaceVertex(int(split[i+offset+1])))
                    offset += int(split[0]) + 1
                elif property[0] == 'texcoord':
                    offset += 1
                    for i in range(3):
                        # Create corresponding tex_coords
                        tex_coord = TexCoord().from_array(split[offset:offset+2])
                        offset += 2
                        self.parent.add_tex_coord(tex_coord)
                        faceVertexArray[i].tex_coord = len(self.parent.tex_coords) - 1
                elif property[0] == 'texnumber':
                    current_material = self.parent.materials[int(split[offset])]

            face = Face(*faceVertexArray)
            face.material = current_material
            self.parent.add_face(face)

        self.counter += 1

        if self.counter == self.current_element.number:
            self.next_element()

    def next_element(self):
        self.element_index += 1
        if self.element_index < len(self.parent.elements):
            self.current_element = self.parent.elements[self.element_index]

class PLYLittleEndianContentParser:
    def __init__(self, parent):
        self.parent = parent
        self.previous_bytes = b''
        self.element_index = 0
        self.counter = 0
        self.current_element = None
        self.started = False

        # Serves for debugging purposes
        # self.current_byte = 0

    def parse_bytes(self, bytes, byte_counter):

        if not self.started:
            # self.current_byte = byte_counter
            self.started = True

        if self.current_element is None:
            self.current_element = self.parent.elements[0]

        bytes = self.previous_bytes + bytes
        current_byte_index = 0

        while True:
            property_values = []

            beginning_byte_index = current_byte_index

            for property in self.current_element.properties:

                size = ply_type_size(property[1])

                if current_byte_index + size[0] > len(bytes):
                    self.previous_bytes = bytes[beginning_byte_index:]
                    # self.current_byte -= len(self.previous_bytes)
                    return

                if len(size) == 1:

                    size = size[0]

                    current_property_bytes = bytes[current_byte_index:current_byte_index+size]
                    property_values.append(bytes_to_element(property[1], current_property_bytes))
                    current_byte_index += size
                    # self.current_byte += size

                elif len(size) == 2:

                    types = property[1].split()[1:]
                    current_property_bytes = bytes[current_byte_index:current_byte_index+size[0]]
                    number_of_elements = bytes_to_element(types[0], current_property_bytes)
                    current_byte_index += size[0]
                    # self.current_byte += size[0]

                    property_values.append([])

                    # Parse list
                    for i in range(number_of_elements):

                        if current_byte_index + size[1] > len(bytes):

                            self.previous_bytes = bytes[beginning_byte_index:]
                            # self.current_byte -= len(self.previous_bytes)
                            return

                        current_property_bytes = bytes[current_byte_index:current_byte_index+size[1]]
                        property_values[-1].append(bytes_to_element(types[1], current_property_bytes))
                        current_byte_index += size[1]
                        # self.current_byte += size[1]


                else:
                    print('I have not idea what this means', file=sys.stderr)

            # Add element
            if self.current_element.name == 'vertex':
                self.parent.add_vertex(Vertex().from_array(property_values))


            elif self.current_element.name == 'face':

                # Create texture coords
                for i in range(0,6,2):
                    tex_coord = TexCoord(*property_values[1][i:i+2])
                    self.parent.add_tex_coord(tex_coord)

                face = Face(\
                    FaceVertex(property_values[0][0], len(self.parent.tex_coords)-3), \
                    FaceVertex(property_values[0][1], len(self.parent.tex_coords)-2), \
                    FaceVertex(property_values[0][2], len(self.parent.tex_coords)-1))

                face.material = self.parent.materials[property_values[2]]

                self.parent.add_face(face)

                pass

            self.counter += 1

            if self.counter == self.current_element.number:
                self.next_element()

    def next_element(self):
        self.counter = 0
        self.element_index += 1
        if self.element_index < len(self.parent.elements):
            self.current_element = self.parent.elements[self.element_index]



class PLYBigEndianContentParser(PLYLittleEndianContentParser):
    def __init__(self, parent):
        super().__init__(self, parent)

    def parse_bytes(self, bytes):
        # Reverse bytes, and then
        super().parse_bytes(self, bytes)

class PLYExporter(Exporter):
    def __init__(self, model):
        super().__init__(model)

    def __str__(self):

        faces = sum([part.faces for part in self.model.parts], [])

        # Header
        string = "ply\nformat ascii 1.0\ncomment Automatically gnerated by model-converter\n"

        # Types : vertices
        string += "element vertex " + str(len(self.model.vertices)) +"\n"
        string += "property float x\nproperty float y\nproperty float z\n"

        # Types : faces
        string += "element face " + str(len(faces)) + "\n"
        string += "property list uint8 int32 vertex_indices\n"

        # End header
        string += "end_header\n"

        # Content of the model
        for vertex in self.model.vertices:
            string += str(vertex.x) + " " + str(vertex.y) + " " + str(vertex.z) + "\n"

        for face in faces:
            string += "3 " + str(face.a.vertex) + " " + str(face.b.vertex) + " " + str(face.c.vertex) + "\n"

        return string

