#!/usr/bin/env python

import os.path
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

setup(name='Tablesplitter',
      version='0.0.1',
      description='Extract data from tables in image PDFs.',
      long_description=readme,
      author='Geoff Hing',
      author_email='geoffhing@gmail.com',
      url='https://github.com/ghing/tablesplitter',
      packages=find_packages(),
      include_package_data=True,
      scripts=['bin/tsplit.py'],
      install_requires=[
          'pillow>=2.4',
          'blinker>=1.3',
          'peewee>=2.2.4',
          'six>=1.6',
          'restless>=2',
          'flask>=0.10',
      ],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Framework :: Flask',
          ],
     )
