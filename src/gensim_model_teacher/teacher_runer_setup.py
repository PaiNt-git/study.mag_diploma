from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='teacher_runer',
    ext_modules=cythonize('teacher_runer.py'),
)
