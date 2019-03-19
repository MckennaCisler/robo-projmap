from distutils.core import setup, Extension

module1 = Extension(
    'draw',
    sources = ['playground.cpp', 'common/shader.cpp'],
    libraries = ['GL', 'GLU', 'GLEW', 'glut', 'glfw'],
    library_dirs = ['/usr/local/lib'])

# module1 = Extension(
#     'draw',
#     sources = ['playground.cpp'])

setup (name = 'draw',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
