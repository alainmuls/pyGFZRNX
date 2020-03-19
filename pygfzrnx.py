#!/usr/bin/env python

import os
import argparse
import sys
from termcolor import colored
import logging
import json
from json import encoder

import am_config as amc
from ampyutils import location, amutils
from gfzrnx import rnx_observation as rnxobs

__author__ = 'amuls'

class prn_action(argparse.Action):
    def __call__(self, parser, namespace, PRNs, option_string=None):
        for prn in PRNs:
            if not 0 < int(prn) < 37 or prn == 'all':
                raise argparse.ArgumentError(self, "PRNs must be in 1..36")
        setattr(namespace, self.dest, PRNs)


class logging_action(argparse.Action):
    def __call__(self, parser, namespace, log_actions, option_string=None):
        print(type(log_actions))
        print(log_actions)
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        for log_action in log_actions:
            if log_action not in choices:
                raise argparse.ArgumentError(self, "log_actions must be in {!s}".format(choices))
        setattr(namespace, self.dest, log_actions)


def treatCmdOpts(argv):
    """
    Treats the command line options and sets the global variables according to the CLI args

    :param argv: the options (without argv[0])
    :type argv: list of string
    """
    helpTxt = os.path.basename(__file__) + ' reads RINEX observation files and creates / plots observables (or comparisons)'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('-r', '--obsRnx', help='rinex observation file', required=True, type=str)
    parser.add_argument('-d', '--dirRnx', help='Directory of SBF file (default {:s})'.format(colored('./', 'green')), required=False, default='.', type=str)

    parser.add_argument('-o', '--obs_type', help='select observation types to plot (default {:s})'.format(colored('C', 'green')), default='C', choices=['C', 'S', 'D', 'L'], nargs='+', type=str)
    parser.add_argument('-s', '--sat_syst', help='select GNNSs (default to {:s})'.format(colored('E', 'green')), default='E', choices=['E', 'G'], nargs='+', type=str)
    parser.add_argument('-p', '--prn', help='select PRNs (default {:s})'.format(colored('all', 'green')), action=prn_action, nargs='+')


    parser.add_argument('-l', '--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], action=logging_action)

    # parser.add_argument('-l', '--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])

    args = parser.parse_args()

    return args.obsRnx, args.dirRnx, args.obs_type, args.sat_syst, args.prn, args.logging


def checkArguments(logger: logging.Logger):
    """
    checks validity of the arguments and changes workind directory
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # change to the directory dirRnx if it exists
    workDir = os.getcwd()
    if amc.dRTK['rinex']['dir'] != '.':
        workDir = os.path.normpath(os.path.join(workDir, amc.dRTK['rinex']['dir']))
    logger.info('{func:s}: working directory is {dir:s}'.format(func=cFuncName, dir=colored('{:s}'.format(workDir), 'green')))

    if not os.path.exists(workDir):
        logger.error('{func:s}: directory {dir:s} does not exists.'.format(func=cFuncName, dir=colored(workDir, 'red')))
        sys.exit(amc.E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)
        logger.info('{func:s}: changed to directory {dir:s}'.format(func=cFuncName, dir=colored('{:s}'.format(workDir), 'green')))

    # check existence of RINEX observation file
    if not os.access(amc.dRTK['rinex']['obs_name'], os.R_OK):
        logger.error('{func:s}: RINEX observation file {rinex:s} not accessible.\n'.format(func=cFuncName, rinex=colored('{!s}'.format(amc.dRTK['rinex']['obs_name']), 'red')))
        return amc.E_FILE_NOT_EXIST
    logger.info('{func:s}: RINEX observation file {obs:s} accessible'.format(func=cFuncName, obs=colored('{!s}'.format(amc.dRTK['rinex']['obs_name']), 'green')))


def main(argv):
    """
    creates a combined SBF file from hourly or six-hourly SBF files
    """
    amc.cBaseName = colored(os.path.basename(__file__), 'yellow')
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    obsRnx, dirRnx, obs_types, sat_systs, prns, logLevels = treatCmdOpts(argv)

    # store cli parameters
    amc.dRTK = {}
    dObs = {}
    amc.dRTK['obs'] = dObs

    dRnx = {}
    dRnx['dir'] = dirRnx
    dRnx['obs_name'] = obsRnx
    dRnx['obs_types'] = obs_types
    dRnx['sat_systs'] = sat_systs
    dRnx['prns'] = prns

    amc.dRTK['rinex'] = dRnx

    # create logging for better debugging
    logger = amc.createLoggers(os.path.basename(__file__), dir=dirRnx, logLevels=logLevels)
    # locate the gfzrnx program used for execution
    dProgs = {}
    dProgs['gfzrnx'] = location.locateProg('gfzrnx', logger)
    amc.dRTK['progs'] = dProgs

    # check arguments
    checkArguments(logger=logger)

    # read the header info using gfzrnx
    amc.dRTK['obs']['header'] = rnxobs.rnxobs_header_metadata(dRnx=amc.dRTK['rinex'], dProgs=amc.dRTK['progs'], logger=logger)
    # extract parts of the rinex observation header
    rnxobs.rnxobs_metadata_parser(dObsHdr=amc.dRTK['obs']['header'], logger=logger)

    # show the information JSON structure
    logger.info('{func:s}: info dictionary = \n{prt!s}'.format(prt=amutils.pretty(amc.dRTK), func=cFuncName))


if __name__ == "__main__":
    main(sys.argv)
