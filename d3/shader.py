#!/usr/bin/env python3

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

import OpenGL.GL as gl
import OpenGL.GL.shaders as sh

class DefaultShader:

    def __init__(self, vertex_path = None, fragment_path = None):

        if vertex_path is None:
            vertex_path = dir_path + '/../assets/shaders/shader.vert'
        if fragment_path is None:
            fragment_path = dir_path + '/../assets/shaders/shader.frag'


        with open(vertex_path) as f:
            self.vertex_src = f.read()

        with open(fragment_path) as f:
            self.fragment_src = f.read()

        self.compile_shaders()
        self.compile_program()


    def compile_shaders(self):
        self.vertex_shader = sh.compileShader(self.vertex_src, gl.GL_VERTEX_SHADER)
        self.fragment_shader = sh.compileShader(self.fragment_src, gl.GL_FRAGMENT_SHADER)

    def compile_program(self):
        self.program = sh.compileProgram(self.vertex_shader, self.fragment_shader)

    def bind(self):
        gl.glUseProgram(self.program)

    def unbind(self):
        gl.glUseProgram(0)
        pass
