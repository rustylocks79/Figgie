from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='Figgie',
    version='1.0',
    packages=[''],
    url='',
    license='',
    author='jerem',
    author_email='',
    description='',
    ext_modules=cythonize('test.pyx', compiler_directives={'language_level' : "3"})
)
