#!/usr/bin/env python

class Material:


    def __init__(self, name):
        self.name = name
        self.Ka = None
        self.Kd = None
        self.Ks = None
        self.map_Kd = None
        self.id = None

    def init_texture(self):

        import OpenGL.GL as gl

        # Already initialized
        if self.id is not None:
            return

        # If no map_Kd, nothing to do
        if self.map_Kd is None:
            return

        try:
            ix, iy, image = self.map_Kd.size[0], self.map_Kd.size[1], self.map_Kd.tobytes("raw", "RGBA", 0, -1)
        except SystemError:
            ix, iy, image = self.map_Kd.size[0], self.map_Kd.size[1], self.map_Kd.tobytes("raw", "RGBX", 0, -1)

        self.id = gl.glGenTextures(1)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, 3, ix, iy, 0,
            gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image
        )

    def bind(self):
        from OpenGL import GL as gl

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)

    def unbind(self):
        from OpenGL import GL as gl

        gl.glDisable(gl.GL_TEXTURE_2D)

import PIL.Image

Material.DEFAULT_MATERIAL=Material('')
Material.DEFAULT_MATERIAL.Ka = 1.0
Material.DEFAULT_MATERIAL.Kd = 0.0
Material.DEFAULT_MATERIAL.Ks = 0.0
Material.DEFAULT_MATERIAL.map_Kd = PIL.Image.new("RGBA", (1,1), "white")

class MeshPart:
    def __init__(self, parent):
        self.parent = parent
        self.material = None
        self.vertex_vbo = None
        self.tex_coord_vbo = None
        self.normal_vbo = None
        self.faces = []

    def init_texture(self):
        if self.material is not None:
            self.material.init_texture()

    def add_face(self, face):
        self.faces.append(face)

    def generate_vbos(self):

        from OpenGL.arrays import vbo
        from numpy import array

        # Build VBO
        v = []
        n = []
        t = []

        for face in self.faces:
            v1 = self.parent.vertices[face.a.vertex]
            v2 = self.parent.vertices[face.b.vertex]
            v3 = self.parent.vertices[face.c.vertex]
            v += [[v1.x, v1.y, v1.z], [v2.x, v2.y, v2.z], [v3.x, v3.y, v3.z]]

            if face.a.normal is not None:
                n1 = self.parent.normals[face.a.normal]
                n2 = self.parent.normals[face.b.normal]
                n3 = self.parent.normals[face.c.normal]
                n += [[n1.x, n1.y, n1.z], [n2.x, n2.y, n2.z], [n3.x, n3.y, n3.z]]

            if face.a.tex_coord is not None:
                t1 = self.parent.tex_coords[face.a.tex_coord]
                t2 = self.parent.tex_coords[face.b.tex_coord]
                t3 = self.parent.tex_coords[face.c.tex_coord]
                t += [[t1.x, t1.y], [t2.x, t2.y], [t3.x, t3.y]]

        self.vertex_vbo  = vbo.VBO(array(v, 'f'))

        if len(n) > 0:
            self.normal_vbo  = vbo.VBO(array(n, 'f'))

        if len(t) > 0:
            self.tex_coord_vbo = vbo.VBO(array(t, 'f'))

    def draw(self):

        if self.material is not None:
            self.material.bind()

        if self.vertex_vbo is not None:
            self.draw_from_vbos()
        else:
            self.draw_from_arrays()

        if self.material is not None:
            self.material.unbind()

    def draw_from_vbos(self):

        import OpenGL.GL as gl

        self.vertex_vbo.bind()
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY);
        gl.glVertexPointerf(self.vertex_vbo)
        self.vertex_vbo.unbind()

        if self.normal_vbo is not None:
            self.normal_vbo.bind()
            gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
            gl.glNormalPointerf(self.normal_vbo)
            self.normal_vbo.unbind()

        if self.tex_coord_vbo is not None:

            if self.material is not None:
                self.material.bind()

            self.tex_coord_vbo.bind()
            gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
            gl.glTexCoordPointerf(self.tex_coord_vbo)
            self.tex_coord_vbo.unbind()

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.vertex_vbo.data) * 9)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)


    def draw_from_arrays(self):
        pass

