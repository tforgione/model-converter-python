from .obj import is_obj, OBJParser, OBJExporter
from .ply import is_ply, PLYParser, PLYExporter
from .stl import is_stl, STLParser, STLExporter
from .basemodel import ModelParser, Exporter

def load_model(path, up_conversion = None):
    parser = None

    if is_obj(path):
        parser = OBJParser(up_conversion)
    elif is_ply(path):
        parser = PLYParser(up_conversion)
    elif is_stl(path):
        parser = STLParser(up_conversion)
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
    elif is_stl(path):
        exporter = STLExporter(model)
    else:
        raise Exception("File format not supported")

    return exporter

def convert(input, output, up_conversion = None):
    model = load_model(input, up_conversion)
    exporter = export_model(model, output)
    return str(exporter)

