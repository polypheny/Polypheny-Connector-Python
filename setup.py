import os
from setuptools import setup

version_file = 'polypheny-connector-version.txt'

if not os.path.exists(version_file):
    raise ValueError(f"Version file '{version_file}' not found. Please create the file with the version number.")

with open(version_file, 'r') as f:
    version = f.read().strip()

print(f"Building version: {version}")

if not version.startswith('v'):
    raise ValueError(f"Invalid version format: {version}. Expected format 'v0.0.0'.")

# Strip the 'v' prefix for the version
version = version[1:]

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='polypheny',
    version=version,
    description='Driver for Polypheny',
    long_description=long_description,
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
    packages=['polypheny'],
    install_requires=[
        "polypheny-prism-api==1.9",
    ],
)
