#!/usr/bin/env python3

from .obj import is_obj, OBJParser
from .ply import is_ply, PLYParser

def load_model(path):
    parser = None

    if is_obj(path):
        parser = OBJParser()
    elif is_ply(path):
        parser = PLYParser()
    else:
        raise Exception("File format not supported")

    parser.parse_file(path)

    return parser
