#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2021 The Polypheny Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import os
import sys

from setuptools import setup, find_packages

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
CONNECTOR_SRC_DIR = os.path.join(THIS_DIR, "polypheny")


VERSION = (1, 1, 1, None)  # Default

try:
    with open(
        os.path.join(CONNECTOR_SRC_DIR, "generated_version.py"), encoding="utf-8"
    ) as f:
        exec(f.read())
except Exception:
    with open(os.path.join(CONNECTOR_SRC_DIR, "version.py"), encoding="utf-8") as f:
        exec(f.read())
version = ".".join([str(v) for v in VERSION if v is not None])


# Parse command line flags

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
    name="polypheny",
    version=version,
    description="Polypheny Connector for Python",
    long_description=readme(),
    long_description_content_type='text/markdown',
    author="The Polypheny Project",
    author_email="mail@polypheny.org",
    url="https://polypheny.org/",
    project_urls={
        "Documentation": "https://polypheny.org/documentation/",
        "Code": "https://github.com/polypheny/Polypheny-Connector-Python",
        "Issue tracker": "https://github.com/polypheny/Polypheny-DB/labels/A-python",
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
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    python_requires=">=3.6",
    install_requires=[
         'protobuf>=3.0.0',
    ]
)
