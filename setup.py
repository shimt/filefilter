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

    setup_kwargs.update(dict(
        options={
            "py2exe": {
                "bundle_files": 1,
                "includes": [
                ],
                "excludes": [
                    '_ssl',
                    '_threading_local',
                    '_lzma',
                    '_dummy_thread',
                    'dummy_threading',
                    'getopt',
                    'gzip',
                    'lzma',
                    'py_compile',
                    'quopri',
                    'select',
                    'selectors',
                    'string',
                    'stringprep',
                    'zipfile',
                    'calendar',
                    'distutils',
                    'doctest',
                    'email',
                    'logging',
                    'optparse',
                    'pdb',
                    'pickle',
                    'pyreadline',
                    'unittest',
                ],
                "dll_excludes": [
                ],
            }
        },
        console=['filefilter.py'],
        zipfile=None,
    ))

setup(**setup_kwargs)
