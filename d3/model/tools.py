import os
from importlib import import_module

from . import formats
from .formats import *
from .basemodel import ModelParser, Exporter

from types import ModuleType

supported_formats = []

class ModelType:
    def __init__(self, typename, inner_module):
        self.typename = typename
        self.inner_module = inner_module

    def test_type(self, file):
        return getattr(self.inner_module, 'is_' + self.typename)(file)

    def create_parser(self, *args, **kwargs):
        return getattr(self.inner_module, self.typename.upper() + 'Parser')(*args, **kwargs)

    def create_exporter(self, *args, **kwargs):
        return getattr(self.inner_module, self.typename.upper() + 'Exporter')(*args, **kwargs)

def find_type(filename, supported_formats):
    for type in supported_formats:
        if type.test_type(filename):
            return type

for name in formats.__dict__:
    if isinstance(formats.__dict__[name], ModuleType) and name != 'glob':
        type = ModelType(name, formats.__dict__[name])
        supported_formats.append(type)

def load_model(path, up_conversion = None):
    parser = None
    type = find_type(path, supported_formats)

    if type is None:
        raise Exception("File format not supported")

    parser = type.create_parser(up_conversion)
    parser.parse_file(path)

    return parser

def export_model(model, path):
    exporter = None
    type = find_type(path, supported_formats)

    if type is None:
        raise Exception('File format is not supported')

    exporter = type.create_exporter(model)
    return exporter

def convert(input, output, up_conversion = None):
    model = load_model(input, up_conversion)
    exporter = export_model(model, output)
    return str(exporter)

