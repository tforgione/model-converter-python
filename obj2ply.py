#!/usr/bin/env python3

import argparse
import os

from conv3d.obj import OBJParser
from conv3d.ply import PLYExporter
from functools import partial

def check_path(path, should_exist):
    """ Check that a path (file or folder) exists or not and return it.
    """
    path = os.path.normpath(path)
    if should_exist != os.path.exists(path):
        msg = "path " + ("does not" if should_exist else "already") + " exist: " + path
        raise argparse.ArgumentTypeError(msg)
    return path

def main(args):
    parser = OBJParser()
    parser.parse_file(args.input)
    exporter = PLYExporter(parser)
    result = str(exporter)

    if args.output is None:
        print(result)
    else:
        with open(args.output, 'w') as f:
            f.write(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('-i', '--input', metavar='input',
                        type=partial(check_path, should_exist=True), default=None,
                        help='Input file (.obj)')
    parser.add_argument('-o', '--output', metavar='output',
                        help='Output path')
    args = parser.parse_args()
    args.func(args)

