from distutils.core import setup

setup(name='polypheny',
      version='0.2',
      description='Driver for Polypheny',
      packages=['polypheny'],
      install_requires=[
          "polypheny-prism-api",
      ],
      )
