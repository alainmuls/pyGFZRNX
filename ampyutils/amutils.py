from __future__ import print_function

import sys
import errno
import os
from termcolor import colored
import webcolors
import gzip
import shutil
import logging
from pandas import DataFrame

from GNSS import gpstime

__author__ = 'amuls'


def mkdir_p(path):
    """
    python implementation of mkdir -p for bash

    :param path: path to create
    :type path: string
    """
    try:
        # print('path = %s' % path)
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def CheckFile(filename, verbose=False):
    """
    check if a file exists

    :param filename: name of file to check
    :type filename: string
    """
    if not os.path.isfile(filename):
        if verbose:
            sys.stderr.write('File %s does not exists. \n' % filename)
        return False
    else:
        return True


def CheckDir(directory, verbose=False):
    """
    check if a directory exists

    :param directory: name of directory to check
    :type directory: string
    """
    if not os.path.isdir(directory):
        if verbose:
            sys.stderr.write('Directory %s does not exists. \n' % directory)
        return False
    else:
        return True


def changeDir(directory, verbose=False):
    """
    check if directory exists and change to it, else abort

    :param directory: name of directory to check
    :type directory: string
    """
    # change to the directory if it exists
    workDir = os.getcwd()
    # if directory[0] is not '.':
    #    print('in if %s' % workDir)
    workDir = os.path.normpath(os.path.join(workDir, directory))

    # print('workDir = %s' % workDir)
    if not os.path.exists(workDir):
        if verbose:
            sys.stderr.write('Directory %s does not exists.\n' % workDir)
        return False
    else:
        os.chdir(workDir)
        return True


def changeDirCheckFile(directory, filename, verbose=False):
    """
    changeDirCheckFile checks whether the directory and file exist

    :param directory: name of directory to check
    :type directory: string
    :param filename: name of file to check
    :type filename: string
    :returns: True or False
    """
    if changeDir(directory, verbose):
        return CheckFile(filename, verbose)
    else:
        return False


def get_filebasename(path):
    """
    Gets a files basename (without extension) from a provided path
    """
    filename = path.split(os.pathsep)[-1].split(os.extsep)[0]
    return filename


def printHeadTailDataFrame(df, name='DataFrame', head=10, tail=10, index=True):
    """
    printHeadTailDataFrame prints the head first/tail last rows of the dataframe df

    :param df: dataframe to print
    :type df: dataframe
    :param name: name for dataframe (def ``DataFrame``)
    :type name: string
    :param head: nr of lies from start of df
    :type head: int
    :param tail: nr of lies from start of df
    :type tail: int
    :param index: display th eindex of the dataframe or not
    :type: bool
    """
    if df.shape[0] <= (head + tail):
        print('\n   ...  %s (size %d)\n%s' % (colored(name, 'green'), df.shape[0], df.to_string(index=index)))
    else:
        print('\n   ... Head of %s (size %d)\n%s' % (colored(name, 'green'), df.shape[0], df.head(n=head).to_string(index=index)))
        print('   ... Tail of %s (size %d)\n%s' % (colored(name, 'green'), df.shape[0], df.tail(n=tail).to_string(index=index)))


def logHeadTailDataFrame(logger: logging.Logger, callerName: str, df: DataFrame, dfName: str = 'DataFrame', head: int = 10, tail: int = 10, index: bool = True):
    """
    logHeadTailDataFrame logs the head first/tail last rows of the dataframe df

    :param df: dataframe to log
    :type df: dataframe
    :param name: name for dataframe (def ``DataFrame``)
    :type name: string
    :param head: nr of lies from start of df
    :type head: int
    :param tail: nr of lies from start of df
    :type tail: int
    :param index: display th eindex of the dataframe or not
    :type: bool
    """
    # cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    if df.shape[0] <= (head + tail):
        logger.info('{func:s}: dataframe {dfname:s} (#{shape:d})\n{df:s}'.format(func=callerName, dfname=colored(dfName, 'green'), shape=df.shape[0], df=df.to_string(index=index)))
    else:
        logger.info('{func:s}: head of dataframe {dfname:s} (#{shape:d})\n{df:s}'.format(func=callerName, dfname=colored(dfName, 'green'), shape=df.shape[0], df=df.head(n=head).to_string(index=index)))
        logger.info('{func:s}: tail of dataframe {dfname:s} (#{shape:d})\n{df:s}'.format(func=callerName, dfname=colored(dfName, 'green'), shape=df.shape[0], df=df.tail(n=tail).to_string(index=index)))


def get_spaced_colors(n):
    """
    getSpacedColors gets the colors spaced in the list of cnames

    :param n: number of colors to cylce through
    :type n: int
    :returns color: list of minimum size n
    :rtype color: list
    """
    max_value = 16581375  # 255**3
    interval = int(max_value / n)
    colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]

    return [(int(i[:2], 16), int(i[2:4], 16), int(i[4:], 16)) for i in colors]


def closest_colour(requested_colour):
    """
    closest_colour searches in color space for the closest named color. It matches by Euclidian distance in the RGB space.

    :param requested_colour: RGB representation of a color
    :int requested_colour: tuple
    :returns min_colours: closest normalised color
    :rtype min_colours: tuple
    """
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    """
    get_colour_name gets the normalised name of the colour or its closest neigbour in RGB space with a normalised name

    :param requested_colour: RGB representation of a color
    :int requested_colour: tuple
    :returns actual_name: normalised name of actual color
    :rtype actual_name: string
    :returns closest_name: normalised name of closest color
    :rtype closest_name: string
    """
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


def dump(obj, nested_level=0, output=sys.stdout):
    """
    dumps a dictionary or list to the output

    :param obj: object to dump
    :type obj: dictionary or list
    :param nested_level: how depp to nest the levels of the object
    :type nested_level: int
    :param output: where to write output to
    :type output: filedescriptor
    """
    spacing = '   '
    if type(obj) == dict:
        print(('%s{' % ((nested_level) * spacing)), file=output)
        for k, v in obj.items():
            if hasattr(v, '__iter__') and type(v) is not str:
                print('%s%s:' % ((nested_level + 1) * spacing, k), file=output)
                dump(v, nested_level + 1, output)
            else:
                print('%s%s: %s' % ((nested_level + 1) * spacing, k, v), file=output)
        print(('%s}' % (nested_level * spacing)), file=output)
    elif type(obj) == list:
        print(('%s[' % ((nested_level) * spacing)), file=output)
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v, nested_level + 1, file=output)
            else:
                print('%s%s' % ((nested_level + 1) * spacing, v), file=output)
        print(('%s]' % ((nested_level) * spacing)), file=output)
    else:
        print(('%s%s' % (nested_level * spacing, obj)), file=output)


def line_num_for_phrase_in_file(phrase='the dog barked', filename='file.txt'):
    """
    line_num_for_phrase_in_file gets the line number for a sentence in a file

    :param phrase: phrase to search for
    :type phrase: string
    :param filename: name of file to search in
    :type filename: string
    :returns: linenumber of searched text, if not founf returns -1
    :rtype: int
    """
    with open(filename, 'r') as f:
        for (i, line) in enumerate(f):
            if phrase in line:
                return i
    return -1


def hms2sec(x):
    """
    hms2sec converts a string in HH:MM:SS.SS into a float value

    :param x: time expressed as HH:MM:SS.SS
    :type x: string
    :returns: number of seconds
    :rtype: float
    """
    times = x.split(':')
    return (60 * float(times[0]) + float(times[1])) * 60 + float(times[2])


def tow2sod(x):
    """
    tow2sec converts a string in TOW into a float value

    :param x: time expressed as TOW
    :type x: string
    :returns: number of seconds
    :rtype: float
    """
    return(x % gpstime.SECSINDAY)


def count_lines(filename):
    f = open(filename)
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read  # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    # print('lines = {}'.format(lines))
    return lines


def decompress(fileCompName: str, fileName: str):
    """
    decompresses fileCompName
    """
    with open(fileName, 'wb') as f_out, gzip.open(fileCompName, 'rb') as f_in:
        shutil.copyfileobj(f_in, f_out)


def make_rgb_transparent(rgb, bg_rgb, alpha):
    """
    make a color transparent
    """
    return [alpha * c1 + (1 - alpha) * c2
            for (c1, c2) in zip(rgb, bg_rgb)]


def pretty(value, htchar='\t', lfchar='\n', indent=0):
    nlch = lfchar + htchar * (indent + 1)
    if type(value) is dict:
        items = [
            nlch + repr(key) + ': ' + pretty(value[key], htchar, lfchar, indent + 1)
            for key in value
        ]
        return '{%s}' % (','.join(items) + lfchar + htchar * indent)
    elif type(value) is list:
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '[%s]' % (','.join(items) + lfchar + htchar * indent)
    elif type(value) is tuple:
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + lfchar + htchar * indent)
    else:
        return repr(value)


def delete_lines(original_file: str, lst_line_number: list):
    """
    Delete lines from a file where line number  is in given list
    """
    is_skipped = False
    current_index = 1
    dummy_file = original_file + '.bak'

    # print('lst_line_number = {!s}'.format(lst_line_number))
    # print('type lst_line_number = {!s}'.format(type(lst_line_number)))

    # Open original file in read only mode and dummy file in write mode
    with open(original_file, 'r') as read_obj, open(dummy_file, 'w') as write_obj:
        # Line by line copy data from original file to dummy file
        for line in read_obj:
            # If current line number matches the given line number then skip copying
            # print('true = {!s}'.format(current_index in lst_line_number))
            if not current_index in lst_line_number:
                write_obj.write(line)
            else:
                is_skipped = True

            current_index += 1

    # If any line is skipped then rename dummy file as original file
    if is_skipped:
        os.remove(original_file)
        os.rename(dummy_file, original_file)
    else:
        os.remove(dummy_file)


def DT_convertor(o):
    if isinstance(o, datetime):
        return o.__str__()
