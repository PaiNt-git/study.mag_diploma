from setuptools import setup
from Cython.Build import cythonize

setup(
    name='teacher',
    ext_modules=cythonize("teacher.pyx", language_level=3)
)
