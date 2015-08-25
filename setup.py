#! /usr/bin/env python3
# coding: utf-8

import platform

from setuptools import setup

setup_kwargs = dict(
    name='filefilter',
    version='1.0',
    description='File Filtering Tool',
    author='Shinichi MOTOKI',
    author_email='shinichi-motoki@overruns.org',
    url='http://gitlab.overruns.org/shinichi-motoki/filefilter',
    scripts=['filefilter.py'],
)

if platform.system() == 'Windows':
    import py2exe

    setup_kwargs.extend(dict(
        options={
            "py2exe": {
                "bundle_files": 1,
                "includes": [
                ],
                "excludes": [
                    'unittest', 'pyreadline', 'email', 'logging', '_ssl',
                    'pickle', 'pdb', 'optparse', 'doctest', 'calendar',
                    'bz2', 'distutils',
                ],
                "dll_excludes": [
                ],
            }
        },
        console=['filefilter.py'],
        zipfile=None,
    ))

setup(**setup_kwargs)
