from distutils.core import setup

setup(name='polypheny',
      version='0.2',
      description='Driver for Polypheny',
      packages=['.'],
      install_requires=[
          "protobuf==4.24.3",
      ],
      )
