#! /usr/bin/env python3
# coding: utf-8

import argparse
import os
import shutil
import subprocess
import sys

from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp


def unique(pathlist):
    uniqued = list()

    [uniqued.append(v) for v in pathlist if v not in uniqued]

    return uniqued


def choose(*args):
    return next(filter(None, args), None)


class FilterException(Exception):
    pass


class FilterProcessException(FilterException):

    def __init__(self, filter_, returncode=None, stderr=None, exception=None):
        self.filter = filter_
        self.returncode = returncode
        self.stderr = stderr
        self.exception = exception


class FilterProcess():

    def __init__(self, caller, filterpath):
        self.caller = caller
        self.filterpath = filterpath

    def run(self, instream, outstream):
        args = list()
        if self.caller is not None:
            args.append(self.caller)
        args.append(self.filterpath)

        try:
            process = subprocess.Popen(
                args,
                stdin=instream,
                stdout=outstream,
                stderr=subprocess.PIPE,
                shell=False,
                universal_newlines=False,
            )
        except FileNotFoundError as e:
            raise FilterProcessException(self, exception=e) from e

        (stdout_, stderr_) = process.communicate()

        if process.returncode != 0:
            raise FilterProcessException(
                self,
                returncode=process.returncode,
                stderr=stderr_)

        if stdout_:
            sys.stdout.flush()
            sys.stdout.buffer.write(stdout_)

        if stderr_:
            sys.stderr.flush()
            sys.stderr.buffer.write(stderr_)

    # Special method

    def __call__(self, instream, outstream):
        self.run(instream, outstream)


class FilterChain():

    def __init__(self, workdir, filters):
        self.workdir = workdir
        self.filters = filters
        self.process_file_hook = list()
        self.call_filter_hook = list()

    def __open_outstream(self, filepath, filterpath):
        prefix = "{0}_{1}_".format(
            Path(filepath).stem,
            Path(filterpath).stem
        )

        return NamedTemporaryFile(
            dir=self.workdir,
            prefix=prefix,
            delete=False,
        )

    def streamfilter(self, filepath, filestream):
        outstream = None
        instream = filestream
        n = 0

        for currentfilter in self.filters:
            outstream = self.__open_outstream(
                filepath, currentfilter.filterpath
            )

            list(map(lambda f: f(filepath,
                                 filestream,
                                 currentfilter,
                                 outstream),
                     self.call_filter_hook))

            currentfilter(instream, outstream)

            if n > 0:
                instream.close()
            instream = outstream
            instream.seek(0)

            n = n + 1

        return instream

    def filefilter(self, filepath):
        laststream = None

        with open(filepath, mode='r+b') as filestream:
            list(map(lambda f: f(filepath,
                                 filestream),
                     self.process_file_hook))

            laststream = self.streamfilter(filepath, filestream)
            filestream.seek(0)
            filestream.truncate()
            shutil.copyfileobj(laststream, filestream)
            laststream.close()


def build_argparser():
    parser = argparse.ArgumentParser(
        description='file filterling tool',
        fromfile_prefix_chars='@'
    )

    parser.add_argument("-f", "--filter", nargs="+", required=True)
    parser.add_argument("-i", "--input", nargs="+")
    parser.add_argument("--caller", help='(override FF_CALLER)')
    parser.add_argument(
        "--filterdir",
        help='set filter search path (override FF_FILTERDIR)'
    )
    parser.add_argument(
        "--workdir",
        help='set working directory (override FF_WORKDIR)'
    )
    parser.add_argument(
        "-p", "--show-progress",
        dest='showprogress',
        action='store_true',
        help='show progress message'
    )
    return parser


def build_workdir(worktopdir):
    return mkdtemp(prefix="filefilter_", dir=worktopdir)


def build_path(filterdir):
    pathlist = list()

    if filterdir:
        pathlist.extend(filterdir.split(os.pathsep))

    if 'PATH' in os.environ:
        pathlist.extend(os.environ['PATH'].split(os.pathsep))

    return os.pathsep.join(pathlist)


def build_filterchain(workdir, caller, filterpaths):
    filters = list()

    for filterpath in filterpaths:
        filters.append(FilterProcess(caller, filterpath))

    return FilterChain(workdir, filters)


def progress_file(filepath, filestream):
    if progress_file.n > 0:
        print('', file=sys.stderr)

    progress_file.n += 1
    print("{0}:".format(filepath), end='', file=sys.stderr)


def progress_filter(filepath, filestream, currentfilter, outstream):
    msg = " {0}".format(Path(currentfilter.filterpath).name)
    print(msg, end='', file=sys.stderr)


def main():
    parser = build_argparser()

    args = parser.parse_args()

    filterpaths = args.filter
    filepaths = args.input

    caller = choose(args.caller, os.getenv('FF_CALLER'))
    worktopdir = choose(args.workdir, os.getenv('FF_WORKDIR'), '.')
    filterdir = choose(args.filterdir, os.getenv('FF_FILTERDIR'))

    if filterdir:
        os.environ['PATH'] = build_path(filterdir)

    workdir = build_workdir(worktopdir)
    filterchain = build_filterchain(workdir, caller, filterpaths)

    if args.showprogress:
        progress_file.n = 0
        filterchain.process_file_hook.append(progress_file)
        filterchain.call_filter_hook.append(progress_filter)

    if filepaths and len(filepaths) > 0:
        for filepath in filepaths:
            filterchain.filefilter(filepath)
    else:
        if args.showprogress:
            print('stdin:', end='', file=sys.stderr)

        laststream = filterchain.streamfilter('STDIN', sys.stdin.buffer)
        shutil.copyfileobj(laststream, sys.stdout.buffer)
        laststream.close()

    if args.showprogress:
        print('', file=sys.stderr)

    shutil.rmtree(workdir)

if __name__ == '__main__':
    r = 0

    try:
        main()
    except FilterException as e:
        if e.returncode is not None:
            print('\nFilter Error: exit {0}'.format(e.returncode),
                  file=sys.stderr)
            sys.stderr.flush()
            sys.stderr.buffer.write(e.stderr)
            r = e.returncode
        elif e.exception is not None:
            print('\nFilter Error: {0}'.format(e.exception.args[1]),
                  file=sys.stderr)

    sys.exit(r)
