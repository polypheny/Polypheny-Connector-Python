import os
import sys
from setuptools import setup, find_packages

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
CONNECTOR_SRC_DIR = os.path.join(THIS_DIR, "polypheny")

VERSION = (0, 0, 0, None)  # Default
VERSION = "v0.0.0" # Default


version_file = 'polypheny-connector-version.txt'

# necessary for automated build pipeline
if os.path.exists(version_file):
    with open(version_file, 'r') as f:
        version = f.read().strip()

else:
    version = VERSION
    #raise ValueError(f"Version file '{version_file}' not found. Please create the file with the version number.")


#print(f"Building version: {version}")

if not version.startswith('v'):
    raise ValueError(f"Invalid version format: {version}. Expected format 'v0.0.0'.")

# Strip the 'v' prefix for the version
version = version[1:]


### Parse command line flags

# This list defines the options definitions in a set
options_def = {
    "--debug",
}

# Options is the final parsed command line options
options = {e.lstrip("-"): False for e in options_def}


for flag in options_def:
    if flag in sys.argv:
        options[flag.lstrip("-")] = True
        sys.argv.remove(flag)


def readme():
    with open(os.path.join(THIS_DIR, 'README.md'), encoding="utf-8" ) as f:
        return f.read()


setup(
    name='polypheny',
    version=version,
    description='Driver for Polypheny',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author="The Polypheny Project",
    author_email="mail@polypheny.org",
    url="https://polypheny.com/",
    project_urls={
        "Documentation": "https://docs.polypheny.com/en/latest/drivers/python/overview",
        "Code": "https://github.com/polypheny/Polypheny-Connector-Python",
        "Issue tracker": "https://github.com/polypheny/Polypheny-DB/labels/A-python"
    },
    license="Apache License, Version 2.0",
    packages=find_packages(),
    include_package_data=True,
    command_options={
        'build_sphinx': {
            'version': ('setup.py', version),
            'release': ('setup.py', version),
        },
    },
    python_requires=">=3.8",
    install_requires=[
        "polypheny-prism-api==1.9",
    ],
)
