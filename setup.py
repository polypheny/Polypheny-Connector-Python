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

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
SRC_DIR = os.path.join(THIS_DIR, "src")
CONNECTOR_SRC_DIR = os.path.join(SRC_DIR, "polypheny", "connector")


version = "0.1"

setup(
    name="polypheny-connector-python",
    version=version,
    description="Polypheny connector for Python",
    long_description=readme(),
    author="Polypheny Project",
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
    cmdclass=cmdclass,
    command_options={
        'build_sphinx': {
            'version': ('setup.py', version),
            'release': ('setup.py', version),
        },
    },
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
    ]
)
