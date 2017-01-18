from math import sqrt
from ..geometry import Vector
from .mesh import Material, MeshPart

Vertex = Vector
TexCoord = Vertex
Normal = Vertex
Color = Vertex

class FaceVertex:
    """Contains the information a vertex needs in a face

    In contains the index of the vertex, the index of the texture coordinate
    and the index of the normal. It is None if it is not available.
    """
    def __init__(self, vertex = None, tex_coord = None, normal = None, color = None):
        """Initializes a FaceVertex from its indices
        """
        self.vertex = vertex
        self.tex_coord = tex_coord
        self.normal = normal
        self.color = color

    def from_array(self, arr):
        """Initializes a FaceVertex from an array

        The array can be an array of strings, the first value will be the
        vertex index, the second will be the texture coordinate index, and the
        third will be the normal index.
        """
        self.vertex  = int(arr[0]) if len(arr) > 0 else None

        try:
            self.tex_coord = int(arr[1]) if len(arr) > 1 else None
        except:
            self.tex_coord = None

        try:
            self.normal  = int(arr[2]) if len(arr) > 2 else None
        except:
            self.normal = None

        try:
            self.color  = int(arr[3]) if len(arr) > 3 else None
        except:
            self.color = None

        return self

class Face:
    """Represents a face with 3 vertices

    Faces with more than 3 vertices are not supported in this class. You should
    split your face first and then create the number needed of instances of
    this class.
    """
    def __init__(self, a = None, b = None, c = None, material = None):
        """Initializes a Face with its three FaceVertex and its Material
        """
        self.a = a
        self.b = b
        self.c = c
        self.material = material

    # Expects array of array
    def from_array(self, arr):
        """Initializes a Face with an array

        The array should be an array of array of objects.
        Each array will represent a FaceVertex
        """
        self.a = FaceVertex().from_array(arr[0])
        self.b = FaceVertex().from_array(arr[1])
        self.c = FaceVertex().from_array(arr[2])
        return self

class ModelParser:
    """Represents a 3D model
    """
    def __init__(self, up_conversion = None):
        """Initializes the model
        """
        self.up_conversion = up_conversion
        self.vertices = []
        self.colors = []
        self.normals = []
        self.tex_coords = []
        self.parts = []
        self.current_part = None
        self.bounding_box = BoundingBox()
        self.center_and_scale = True
        self.path = None

    def init_textures(self):
        """Initializes the textures of the parts of the model

        Basically, calls glGenTexture on each texture
        """
        for part in self.parts:
            part.init_texture()

    def add_vertex(self, vertex):
        """Adds a vertex to the current model

        Will also update its bounding box, and convert the up vector if
        up_conversion was specified.
        """
        # Apply up_conversion to the vertex
        new_vertex = vertex
        if self.up_conversion is not None:
            if self.up_conversion[0] == 'y' and self.up_conversion[1] == 'z':
                new_vertex = Vector(vertex.y, vertex.z, vertex.x)
            elif self.up_conversion[0] == 'z' and self.up_conversion[1] == 'y':
                new_vertex = Vector(vertex.z, vertex.x, vertex.y)

        self.vertices.append(new_vertex)
        self.bounding_box.add(new_vertex)

    def add_tex_coord(self, tex_coord):
        """Adds a texture coordinate element to the current model
        """
        self.tex_coords.append(tex_coord)

    def add_normal(self, normal):
        """Adds a normal element to the current model
        """
        self.normals.append(normal)

    def add_color(self, color):
        """Adds a color element to the current model
        """
        self.colors.append(color)

    def add_face(self, face):
        """Adds a face to the current model

        If the face has a different material than the current material, it will
        create a new mesh part and update the current material.
        """
        if self.current_part is None or (face.material != self.current_part.material and face.material is not None):
            self.current_part = MeshPart(self)
            self.current_part.material = face.material if face.material is not None else Material.DEFAULT_MATERIAL
            self.parts.append(self.current_part)

        self.current_part.add_face(face)

    def parse_file(self, path, chunk_size = 512):
        """Sets the path of the model and parse bytes by chunk
        """
        self.path = path
        byte_counter = 0
        with open(path, 'rb') as f:
            while True:
                bytes = f.read(chunk_size)
                if bytes == b'':
                    return
                self.parse_bytes(bytes, byte_counter)
                byte_counter += chunk_size

    def draw(self):
        """Draws each part of the model with OpenGL
        """
        import OpenGL.GL as gl

        if self.center_and_scale:
            center = self.bounding_box.get_center()
            scale = self.bounding_box.get_scale() / 2
            gl.glPushMatrix()
            gl.glScalef(1/scale, 1/scale, 1/scale)
            gl.glTranslatef(-center.x, -center.y, -center.z)

        for part in self.parts:
            part.draw()

        if self.center_and_scale:
            gl.glPopMatrix()

    def generate_vbos(self):
        """Generates the VBOs of each part of the model
        """
        for part in self.parts:
            part.generate_vbos()

    def generate_vertex_normals(self):
        """Generate the normals for each vertex of the model

        A normal will be the average normal of the adjacent faces of a vertex.
        """
        self.normals = [Normal() for i in self.vertices]

        for part in self.parts:
            for face in part.faces:
                v1 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.b.vertex])
                v2 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.c.vertex])
                cross = Vertex.cross_product(v1, v2)
                self.normals[face.a.vertex] += cross
                self.normals[face.b.vertex] += cross
                self.normals[face.c.vertex] += cross

        for normal in self.normals:
            normal.normalize()

        for part in self.parts:
            for face in part.faces:
                face.a.normal = face.a.vertex
                face.b.normal = face.b.vertex
                face.c.normal = face.c.vertex

    def generate_face_normals(self):
        """Generate the normals for each face of the model

        A normal will be the normal of the face
        """
        # Build array of faces
        faces = sum(map(lambda x: x.faces, self.parts), [])
        self.normals = [Normal()] * len(faces)

        for (index, face) in enumerate(faces):

            v1 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.b.vertex])
            v2 = Vertex.from_points(self.vertices[face.a.vertex], self.vertices[face.c.vertex])
            cross = Vertex.cross_product(v1, v2)
            cross.normalize()
            self.normals[index] = cross

            face.a.normal = index
            face.b.normal = index
            face.c.normal = index

class TextModelParser(ModelParser):
    def parse_file(self, path):
        """Sets the path of the model and parse each line
        """
        self.path = path
        with open(path) as f:
            for line in f.readlines():
                line = line.rstrip()
                if line != '':
                    self.parse_line(line)


class BoundingBox:
    """Represents a bounding box of a 3D model
    """
    def __init__(self):
        """Initializes the coordinates of the bounding box
        """
        self.min_x = +float('inf')
        self.min_y = +float('inf')
        self.min_z = +float('inf')

        self.max_x = -float('inf')
        self.max_y = -float('inf')
        self.max_z = -float('inf')

    def add(self, vector):
        """Adds a vector to a bounding box

        If the vector is outside the bounding box, the bounding box will be
        enlarged, otherwise, nothing will happen.
        """
        self.min_x = min(self.min_x, vector.x)
        self.min_y = min(self.min_y, vector.y)
        self.min_z = min(self.min_z, vector.z)

        self.max_x = max(self.max_x, vector.x)
        self.max_y = max(self.max_y, vector.y)
        self.max_z = max(self.max_z, vector.z)

    def __str__(self):
        """Returns a string that represents the bounding box
        """
        return "[{},{}],[{},{}],[{},{}]".format(
            self.min_x,
            self.min_y,
            self.min_z,
            self.max_x,
            self.max_y,
            self.max_z)

    def get_center(self):
        """Returns the center of the bounding box
        """
        return Vertex(
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2)

    def get_scale(self):
        """Returns the maximum edge of the bounding box
        """
        return max(
            abs(self.max_x - self.min_x),
            abs(self.max_y - self.min_y),
            abs(self.max_z - self.min_z))


class Exporter:
    """Represents an object that can export a model into a certain format
    """
    def __init__(self, model):
        self.model = model


