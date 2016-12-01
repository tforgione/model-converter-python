# model-converter

This project aims to be a simple, lightweight, and useful 3D model editor.
For the moment, only `obj` and `ply` ascii models are supported.

Feel free to open an issue if you find anything wrong in this.

# Scripts

A few utilities to manage 3D models :
  - `convert.py` that converts any type of model to any other
  - `viewer.py` which is a simple script that renders a 3d model

# Dependencies

This project is written in python 3. The `convert.py` script is made for
needing nothing else than python. However, the `viewer.py` script has a few
dependencies, you'll need :

  - pip (to install the other dependencies) `sudo apt-get install python3-pip`
    for example
  - numpy `sudo pip install numpy`
  - pygame `sudo pip install pygame`
  - PyOpenGL `sudo pip install pyopengl`

## Supported formats
  - Wavefront `.obj`
  - Stanford `.ply`
  - STL files `.stl`

