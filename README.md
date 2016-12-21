# model-converter

This project aims to be a simple, lightweight, and useful 3D model editor.
For the moment, only `obj`, `off`, `ply` ascii and `stl` models are supported.

Feel free to open an issue if you find anything wrong in this.

  - [Scripts](#scripts)
  - [Install](#install)
  - [Contributing](#contributing)
  - [List of all supported formats](#formats)

# Scripts

A few utilities to manage 3D models :
  - `convert.py` that converts any type of model to any other
  - `viewer.py` which is a simple script that renders a 3d model

# Install

This project is written in python 3. The `convert.py` script is made for
needing nothing else than python. However, the `viewer.py` script has a few
dependencies, you'll need :

  - pip (to install the other dependencies) `sudo apt-get install python3-pip`
    for example
  - PIL `sudo pip install pillow`
  - numpy `sudo pip install numpy`
  - pygame `sudo pip install pygame`
  - PyOpenGL `sudo pip install pyopengl`

## Contributing

If you want to add a new format to this converter, it should be easy enough,
you just have to create a python file in `d3/model/formats` that should :

  - be named after the format you want to add (e.g. `obj.py`)
  - contain a function that tests if a filename is in the specified format (e.g. `is_obj`)
  - contain a parser class (e.g. `OBJParser`)
  - contain an exporter class (e.g. `OBJExporter`)

### About the parser
The parser should inherit the `ModelParser` class in the `basemodel.py` module.
The `ModelParser` class has everything needed to create a 3D model and render it.

### About the exporter
The exporter should inherit the `Exporter` class in the `basemodel.py` module.
It should have a constructor that takes a `ModelParser` has parameter and a
`__str__` method that should compute the export.

## Formats
Here is the list of all the supported formats
  - Wavefront `.obj`
  - Stanford `.ply`
  - Object File Format `.off`
  - STL files `.stl`

