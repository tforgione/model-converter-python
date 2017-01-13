#!/usr/bin/env python3

import sys
import ctypes
import argparse
import os
import math

# Test dependencies
try:
    import PIL
except:
    print('You need to install PIL', file=sys.stderr)
    sys.exit(-1)

try:
    import pygame as pg
    import pygame.locals as pgl
except:
    print('You need to install pygame', file=sys.stderr)
    sys.exit(-1)

try:
    import OpenGL.GL as gl
    import OpenGL.GLU as glu
except:
    print('You need to install pyopengl', file=sys.stderr)
    sys.exit(-1)

try:
    import numpy
except:
    print('You need to install numpy', file=sys.stderr)
    sys.exit(-1)

from d3.model.tools import load_model
from d3.geometry import Vector
from d3.controls import TrackBallControls, OrbitControls
from d3.camera import Camera
from d3.shader import DefaultShader

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 1024

def resize(width, height):
    length = min(width, height)
    offset = int( math.fabs(width - height) / 2)

    # Ugly AF
    pg.display.set_mode((width, height), pg.DOUBLEBUF | pg.RESIZABLE | pg.OPENGL)

    if width < height:
        gl.glViewport(0, offset, length, length)
    else:
        gl.glViewport(offset, 0, length, length)

def main(args):

    if (args.from_up is None) != (args.to_up is None):
        raise Exception("from-up and to-up args should be both present or both absent")

    up_conversion = None
    if args.from_up is not None:
        up_conversion = (args.from_up, args.to_up)

    if args.verbose:
        def log(*args, **kwargs):
            print(*args, **kwargs)
    else:
        def log(*args, **kwargs):
            pass

    # Load and parse the model
    log('Loading model...', file=sys.stderr, end='')
    model = load_model(args.input, up_conversion)
    log(' done!\,Initialiazing OpenGL Context', file=sys.stderr, end='')

    camera = Camera(Vector(0,0,5), Vector(0,0,0))
    controls = OrbitControls()

    pg.init()
    pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pgl.DOUBLEBUF | pgl.OPENGL | pgl.RESIZABLE)
    pg.display.set_caption('Model-Converter')

    # OpenGL init
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(45, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 50.0)

    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_CULL_FACE)
    gl.glEnable(gl.GL_BLEND)
    gl.glClearColor(0, 0, 0, 0)

    running = True


    log(' done!\nInitializing OpenGL textures...', file=sys.stderr, end='')
    # Initializes OpenGL textures
    model.init_textures()

    # Compute normals if not already computed
    if len(model.normals) == 0:
        log(' done!\nComputing normals...', file=sys.stderr, end='')
        model.generate_vertex_normals()

    # Generate vbos for smooth rendering
    log(' done!\nGenerating vbos...', file=sys.stderr, end='')
    model.generate_vbos()

    shader = DefaultShader()

    log(' Done!\nReady!', file=sys.stderr)

    while running:
        for event in pg.event.get():

            controls.apply_event(event)

            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pg.mouse.get_rel()
            elif event.type == pg.VIDEORESIZE:
                resize(event.size[0], event.size[1])

        # Update physics
        controls.update()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        camera.look()

        gl.glPushMatrix()
        controls.apply()

        # gl.glBegin(gl.GL_LINES)
        # gl.glColor3f (1.0,0.0,0.0)
        # gl.glVertex3f(0.0,0.0,0.0)
        # gl.glVertex3f(2.0,0.0,0.0)
        # gl.glColor3f (0.0,1.0,0.0)
        # gl.glVertex3f(0.0,0.0,0.0)
        # gl.glVertex3f(0.0,2.0,0.0)
        # gl.glColor3f (0.0,0.0,1.0)
        # gl.glVertex3f(0.0,0.0,0.0)
        # gl.glVertex3f(0.0,0.0,2.0)
        # gl.glEnd()

        shader.bind()
        model.draw()
        shader.unbind()
        gl.glPopMatrix()

        gl.glFlush()
        pg.display.flip()

        # Sleep
        pg.time.wait(10)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('-i', '--input', metavar='input', default=None, help='Input model')
    parser.add_argument('-fu', '--from-up', metavar='fup', default=None,
                        help="Initial up vector")
    parser.add_argument('-tu', '--to-up', metavar='fup', default=None,
                        help="Output up vector")
    parser.add_argument('-V', '--verbose', default=False, action='store_true',
                        help="Verbose output")

    args = parser.parse_args()
    args.func(args)
