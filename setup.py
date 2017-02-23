# -*- coding: utf-8 -*-

# Imports ###########################################################

import os
from setuptools import setup


# Functions #########################################################

def package_data(pkg, root_list):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


# Main ##############################################################

setup(
    name='xblock-skytap',
    version='0.1',
    description='Skytap XBlock',
    packages=['xblock_skytap'],
    install_requires=[
        'XBlock',
        'xblock-utils',
        'skytap',
    ],
    entry_points={
        'xblock.v1': 'skytap = xblock_skytap:SkytapXBlock',
    },
    package_data=package_data("xblock_skytap", ["public", "templates"]),
)
