#!/usr/bin/env python3

import sys
import ctypes
import pygame
import argparse
import os
import math

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from OpenGL.GLU import *

from d3.model.tools import load_model
from d3.geometry import Vector
from d3.controls import TrackBallControls
from d3.camera import Camera
from d3.shader import DefaultShader

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

def main(args):

    camera = Camera(Vector(0,0,5), Vector(0,0,0))
    controls = TrackBallControls()

    pygame.init()
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    # OpenGL init
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 50.0)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glClearColor(0, 0, 0, 0)

    running = True

    model = load_model(args.input)
    model.generate_vbos()

    shader = DefaultShader()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pygame.mouse.get_rel()

        # Update physics
        controls.update()


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        camera.look()

        glPushMatrix()
        controls.apply()
        shader.bind()
        model.gl_draw()
        shader.unbind()
        glPopMatrix()

        glFlush()
        pygame.display.flip()

        # Sleep
        pygame.time.wait(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('-i', '--input', metavar='input', default=None, help='Input model')
    args = parser.parse_args()
    args.func(args)
