from ..basemodel import ModelParser, Exporter, Vertex, Face, FaceVertex

def is_ply(filename):
    return filename[-4:] == '.ply'

class PLYParser(ModelParser):

    def __init__(self, up_conversion = None):
        super().__init__(up_conversion)
        self.counter = 0
        self.elements = []
        self.inner_parser = PLYHeaderParser(self)

    def parse_line(self, string):
        self.inner_parser.parse_line(string)

class PLYHeaderParser:
    def __init__(self, parent):
        self.current_element = None
        self.parent = parent

    def parse_line(self, string):
        split = string.split()
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
            self.current_element.add_property(split[-1], (split[1:][:-1]))

        elif split[0] == 'end_header':
            self.parent.inner_parser = PLYContentParser(self.parent)


class PLYElement:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.properties = []

    def add_property(self, name, type):
        self.properties.append((name, type))

class PLYVertex(Vertex):
    def __init__(self, string):
        pass

    def add_to_parser(self, parser):
        pass

class PLYContentParser:
    def __init__(self, parent):
        self.parent = parent
        self.element_index = 0
        self.counter = 0
        self.current_element = self.parent.elements[0]

    def parse_line(self, string):

        split = string.split()

        if self.current_element.name == 'vertex':
            self.parent.add_vertex(Vertex().from_array(split))
        elif self.current_element.name == 'face':

            faceVertexArray = []

            # Analyse element
            for property in self.current_element.properties:
                if property[0] == 'vertex_indices':
                    for i in range(int(split[0])):
                        faceVertexArray.append(FaceVertex(int(split[i+1])))

            self.parent.add_face(Face(*faceVertexArray))

        self.counter += 1

        if self.counter == self.current_element.number:
            self.next_element()

    def next_element(self):
        self.element_index += 1
        if self.element_index < len(self.parent.elements):
            self.current_element = self.parent.elements[self.element_index]

class PLYExporter(Exporter):
    def __init__(self, model):
        super().__init__(model)

    def __str__(self):

        faces = sum([part.faces for part in self.model.parts], [])

        # Header
        string = "ply\nformat ascii 1.0\ncomment Automatically gnerated by model-converter\n"

        # Types : vertices
        string += "element vertex " + str(len(self.model.vertices)) +"\n"
        string += "property float32 x\nproperty float32 y\nproperty float32 z\n"

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

