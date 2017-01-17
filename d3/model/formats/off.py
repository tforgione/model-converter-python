from ..basemodel import TextModelParser, Exporter, Vertex, TexCoord, Normal, FaceVertex, Face
from ..mesh import Material, MeshPart

def is_off(filename):
    return filename[-4:] == '.off'

class OFFParser(TextModelParser):
    def __init__(self, up_conversion = None):
        super().__init__(up_conversion)
        self.vertex_number = None
        self.face_number = None
        self.edge_number = None

    def parse_line(self, string):

        split = string.split()

        if string == 'OFF':
            pass
        elif self.vertex_number is None:
            # The first will be the header
            self.vertex_number = int(split[0])
            self.face_number = int(split[1])
            self.edge_number = int(split[2])
        elif len(self.vertices) < self.vertex_number:
            self.add_vertex(Vertex().from_array(split))
        else:
            self.add_face(Face(FaceVertex(int(split[1])), FaceVertex(int(split[2])), FaceVertex(int(split[3]))))



class OFFExporter(Exporter):
    def __init__(self, model):
        super().__init__(model)

    def __str__(self):

        faces = sum(map(lambda x: x.faces, self.model.parts), [])
        string = "OFF\n{} {} {}".format(len(self.model.vertices), len(faces), 0) + '\n'

        for vertex in self.model.vertices:
            string += ' '.join([str(vertex.x), str(vertex.y), str(vertex.z)]) + '\n'

        for face in faces:
            string += '3 ' + ' '.join([str(face.a.vertex), str(face.b.vertex), str(face.c.vertex)]) + '\n'

        return string

