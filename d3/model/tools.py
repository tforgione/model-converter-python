#!/usr/bin/env python3

from .obj import is_obj, OBJParser, OBJExporter
from .ply import is_ply, PLYParser, PLYExporter
from .basemodel import ModelParser, Exporter

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

def export_model(model, path):
    exporter = None

    if is_obj(path):
        exporter = OBJExporter(model)
    elif is_ply(path):
        exporter = PLYExporter(model)
    else:
        raise Exception("File format not supported")

    return exporter

def convert(input, output):
    model = load_model(input)
    exporter = export_model(model, output)
    return str(exporter)

