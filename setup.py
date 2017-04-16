#!/usr/bin/env python3

from setuptools import setup

setup(name='MapGen',
      version='0.1',
      description='An application to generate random stylised maps for games, graphics.',
      url='https://github.com/DarkPurple141/Maps',
      author='Alexander Hinds',
      author_email='alex.hinds141@gmail.com',
      keywords='maps mapmaking fantasy games gui generation',
      install_requires=[
          'pillow', 'pygame', 'numpy', 'triangle',
      ],
      package_data= {'MapGen' : ["words"]},
      license='MIT',
      packages=['MapGen'],
      test_suite='MapGen.tests',
      zip_safe=False)
