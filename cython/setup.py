from setuptools import Extension, setup
from Cython.Build import cythonize

setup(
    name="mupen64plus",
    ext_modules=cythonize([Extension("mupen64plus", ["mupen64plus.pyx"], libraries=["mupen64plus"])]),
)
