filefilter
==========

filefilter is a tool which applies and rewrites a filter to a file.  
I was tired from writing a shell script each time.  

## Description

It is a tool which applies a filter to the specified file.  
This is effective when rewriting a lot of file.  

```console:before
FILTERDIR="${HOME}/filter"
cat example.txt \
	| ${FILTERDIR}/filter1 \
	| ${FILTERDIR}/filter2 \
	| ${FILTERDIR}/filter3 \
	> example.txt.new
mv example.txt.new example.txt
```

```console:after
export FF_FILTERDIR="${HOME}/filter"
python3 filefilter.py \
	-f filter1 filter2 filter3 \
	-i example.txt
```

## Requirement

Python 3.x

## Usage

### Command line

```
filefilter.py [-h] -f FILTER [FILTER ...] [-i INPUT [INPUT ...]]
              [--caller CALLER] [--filterdir FILTERDIR]
              [--workdir WORKDIR]
```

### Environment variable

|     Name     |                        Usage                        | Default |
| :----------- | :-------------------------------------------------- | :------ |
| FF_CALLER    | The program for calling a filter (ex. /usr/bin/env) | None    |
| FF_FILTERDIR | The search path of a filter                         | None    |
| FF_WORKDIR   | The directory which creates a file temporarily      | .       |

### Notes

* FF_FILTERDIR is a PATH environment variable at the time of a filter call.
* set up "FF_CALLER=/usr/bin/env", when you use it by MINGW.
* A temporary directory(filefilter_***) is not deleted when an error occurs.

## Install

copy filefilter.py. or `python setup.py install` or `python setup.py py2exe` (require py2exe)

## Licence

MIT


