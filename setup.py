#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup module.
"""

import io
import os
import re
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

from ecs import VERSION

# Package meta-data.
NAME = 'ecs-tools'
DESCRIPTION = 'Command line tools to interact with your ECS clusters. '
URL = 'https://github.com/flou/ecs-tools'
AUTHORS = {
    'ferrand@ekino.com': 'Lou Ferrand',
}

# What packages are required for this module to be executed?
REQUIRED = [
    'boto3>=1.4.5',
    'click>=6.7',
    'crayons>=0.1.2',
    'pyyaml>=3.12',
]

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = '\n' + f.read()


def _download_url():
    return '{repo}/repository/archive.tar.gz?ref={version}'.format(
        repo=URL, version=VERSION
    )


class PublishCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(HERE, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name=NAME,
    version=re.sub(r'[^\d\.]', '', VERSION),
    packages=find_packages(exclude=['tests', 'cover']),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=', '.join(AUTHORS.values()),
    author_email=', '.join(AUTHORS.keys()),
    install_requires=REQUIRED,
    include_package_data=True,
    url=URL,
    download_url=_download_url(),
    keywords=['ECS', 'AWS'],
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Intended Audience :: Developers',
    ],
    entry_points={
        'console_scripts': ['ecs=ecs.cli:cli']
    },
    cmdclass={
        'publish': PublishCommand,
    }
)
