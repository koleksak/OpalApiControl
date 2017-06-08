#!/usr/bin/env python2

from distutils.core import setup
try:
    import setuptools
except ImportError:
    pass
setup(name='OpalApiControl',
      version='0.1.1',
      description='OPAL-RT RT-LAB API Controller',
      author='Kellen Oleksak',
      url='https://github.com/koleksak/OpalApiControl',
      packages=['OpalApiControl'], install_requires=['dime']
      )



