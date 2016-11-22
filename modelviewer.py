#!/usr/bin/env python3

import sys
import ctypes
import pygame
import argparse
import os
import math

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from conv3d.loadmodel import load_model
from conv3d.model import Vertex


WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

x = -0.5
y = 0.5
width = 1
height = 1

class TrackBallControls:
    def __init__(self):
        self.vertex = Vertex()
        self.theta = 0

    def apply(self):
        glRotatef(self.theta * 180 / math.pi, self.vertex.x, self.vertex.y, self.vertex.z)

    def update(self, time = 10):

        if not pygame.mouse.get_pressed()[0]:
            return

        coeff = 0.001
        move = pygame.mouse.get_rel()

        dV = Vertex(move[1] * time * coeff, move[0] * time * coeff, 0)
        dTheta = dV.norm2()

        if abs(dTheta) < 0.01:
            return

        dV.normalize()

        cosT2 = math.cos(self.theta / 2)
        sinT2 = math.sin(self.theta / 2)
        cosDT2 = math.cos(dTheta / 2)
        sinDT2 = math.sin(dTheta / 2)

        A = cosT2 * sinDT2 * dV + cosDT2 * sinT2 * self.vertex + sinDT2 * sinT2 * Vertex.cross_product(dV, self.vertex)

        self.theta = 2 * math.acos(cosT2 * cosDT2 - sinT2 * sinDT2 * Vertex.dot(dV, self.vertex))

        self.vertex = A
        self.vertex.normalize()



def init_frame():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,0,5,0,0,0,0,1,0)

def main(args):

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

    glLightfv(GL_LIGHT0, GL_POSITION, [10,5,7])
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    running = True

    model = load_model(args.input)

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

        init_frame()

        glPushMatrix()
        controls.apply()
        model.gl_draw()
        glPopMatrix()

        glFlush()
        pygame.display.flip()

        # Update physics
        controls.update()

        pygame.time.wait(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('-i', '--input', metavar='input', default=None, help='Input model')
    args = parser.parse_args()
    args.func(args)
