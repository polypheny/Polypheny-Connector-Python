import os
import sys

from distutils.core import setup

# Retrieve 'VERSION' environment variable, default to '0.0' if not found.
version = os.getenv('VERSION', '0.0')

# Attempt to split the version number, default to '0' for both if it fails
try:
    major, minor = version.split('.')
except ValueError:
    major, minor = '0', '0'  # Default to '0.0' if the version isn't in a 'major.minor' format

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(name='polypheny',
      version=version,
      description='Driver for Polypheny',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=['polypheny'],
      install_requires=[
          "polypheny-prism-api==1.6",
      ],
      )
