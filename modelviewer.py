#!/usr/bin/env python3

import sys
import ctypes
import pygame
import argparse
import os

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from conv3d.loadmodel import load_model


WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

x = -0.5
y = 0.5
width = 1
height = 1

def init_frame():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5,5,5,0,0,0,0,1,0)

def main(args):

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

        init_frame()
        model.gl_draw()
        glFlush()
        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('-i', '--input', metavar='input', default=None, help='Input model')
    args = parser.parse_args()
    args.func(args)
