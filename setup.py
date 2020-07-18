from distutils.core import setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext

import Cython.Compiler.Options
from setuptools import Extension

Cython.Compiler.Options.annotate = True

extensions = [
    Extension(name='*', sources=['*.pyx']),
]

setup(
    name='Figgie',
    version='1.0',
    packages=[''],
    url='',
    license='',
    author='jerem',
    author_email='',
    description='',
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}, annotate=True, build_dir='build')
)
