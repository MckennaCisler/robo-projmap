from distutils.core import setup, Extension

module1 = Extension(
    'project',
    sources = ['project.cpp', 'common/shader.cpp'],
    libraries = ['GL', 'GLU', 'GLEW', 'glut', 'glfw'],
    library_dirs = ['/usr/local/lib'])

setup (name = 'project',
       version = '1.0',
       description = 'This is a package to convert from an XYD image coordinates to projector coordinates using a conversion matrix',
       ext_modules = [module1])
