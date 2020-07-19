from setuptools import Extension
from distutils.core import setup
from Cython.Build import cythonize

CYTHON = True

if CYTHON:
    import Cython.Compiler.Options
    Cython.Compiler.Options.annotate = False

    extensions = [
        Extension(name='*', sources=['*.pyx']),
    ]

    setup(
        name='Figgie',
        version='1.0',
        packages=['Figgie'],
        url='',
        license='',
        author='jeremy',
        author_email='',
        description='',
        ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}, annotate=True, build_dir='build')
    )
else:
    setup(
        name='Figgie',
        version='1.0',
        packages=['Figgie'],
        url='',
        license='',
        author='jeremy',
        author_email='',
        description='',
    )
