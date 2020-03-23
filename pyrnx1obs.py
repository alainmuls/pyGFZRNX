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
from gfzrnx import rnx_obs_header, rnx_obs_analyse

__author__ = 'amuls'

class prn_action(argparse.Action):
    def __call__(self, parser, namespace, PRNs, option_string=None):
        for prn in PRNs:
            try:
                if not 0 < int(prn) < 37:
                    raise argparse.ArgumentError(self, "PRNs must be in 1..36 or 'all'")
            except ValueError:
                if prn != 'all':
                    raise argparse.ArgumentError(self, "PRNs must be in 1..36 or 'all'")
        if prn == 'all':
            ret_prns = [prn for prn in range(1, 37)]
            setattr(namespace, self.dest, ret_prns)
        else:
            ret_prns = [int(iprn) for iprn in PRNs]
            setattr(namespace, self.dest, ret_prns)


class logging_action(argparse.Action):
    def __call__(self, parser, namespace, log_actions, option_string=None):
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        for log_action in log_actions:
            if log_action not in choices:
                raise argparse.ArgumentError(self, "log_actions must be in {!s}".format(choices))
        setattr(namespace, self.dest, log_actions)


class freq_action(argparse.Action):
    def __call__(self, parser, namespace, freqs, option_string=None):
        for freq in freqs:
            if freq not in ['1', '2', '5', '6'] and freq != 'all':
                raise argparse.ArgumentError(self, "freqs must be either 1, 2, 5, 6 or 'all'")
        if freqs == ['all']:
            ret_freqs = ['1', '2', '5', '6']
        else:
            ret_freqs = freqs
        setattr(namespace, self.dest, ret_freqs)


class interval_action(argparse.Action):
    def __call__(self, parser, namespace, interval, option_string=None):
        if 60 <= interval <= 1800:
            setattr(namespace, self.dest, interval)
        else:
            raise argparse.ArgumentError(self, "interval must be in [60 .. 1800] seconds")


def treatCmdOpts(argv):
    """
    Treats the command line options and sets the global variables according to the CLI args

    :param argv: the options (without argv[0])
    :type argv: list of string
    """
    helpTxt = os.path.basename(__file__) + ' reads 1 RINEX observation file and creates / plots observables (including differences)'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('-r', '--obsRnx', help='rinex observation file', required=True, type=str)
    parser.add_argument('-d', '--dirRnx', help='Directory of SBF file (default {:s})'.format(colored('./', 'green')), required=False, default='.', type=str)

    parser.add_argument('-o', '--obs_type', help='select observation types to plot (default {:s})'.format(colored('C', 'green')), default='C', choices=['C', 'S', 'D', 'L'], nargs='+', type=str)
    parser.add_argument('-s', '--sat_syst', help='select GNNSs (default to {:s})'.format(colored('E', 'green')), default='E', choices=['E', 'G'], nargs='+', type=str)
    parser.add_argument('-f', '--freqs', help='select frequency bands (default to {:s})'.format(colored('all', 'green')), default='all', nargs='+', action=freq_action)
    parser.add_argument('-p', '--prn', help='select PRNs (default {:s})'.format(colored('all', 'green')), default='all', action=prn_action, nargs='+')

    parser.add_argument('-i', '--interval', help='interval in sec for scanning observation file (default {interval:s} s)'.format(interval=colored(600, 'green')), default=600, type=int, required=False, action=interval_action)

    parser.add_argument('-l', '--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], action=logging_action)

    # parser.add_argument('-l', '--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])

    args = parser.parse_args()

    return args.obsRnx, args.dirRnx, args.obs_type, args.sat_syst, args.freqs, args.prn, args.interval, args.logging


def checkArguments(logger: logging.Logger):
    """
    checks validity of the arguments and changes workind directory
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # change to the directory dirRnx if it exists
    workDir = os.getcwd()
    if amc.dRTK['args']['dir'] != '.':
        workDir = os.path.normpath(os.path.join(workDir, amc.dRTK['args']['dir']))
    logger.info('{func:s}: working directory is {dir:s}'.format(func=cFuncName, dir=colored('{:s}'.format(workDir), 'green')))

    if not os.path.exists(workDir):
        logger.error('{func:s}: directory {dir:s} does not exists.'.format(func=cFuncName, dir=colored(workDir, 'red')))
        sys.exit(amc.E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)
        logger.info('{func:s}: changed to directory {dir:s}'.format(func=cFuncName, dir=colored('{:s}'.format(workDir), 'green')))

    # check existence of RINEX observation file
    if not os.access(amc.dRTK['args']['obs_name'], os.R_OK):
        logger.error('{func:s}: RINEX observation file {rinex:s} not accessible.\n'.format(func=cFuncName, rinex=colored('{!s}'.format(amc.dRTK['args']['obs_name']), 'red')))
        return amc.E_FILE_NOT_EXIST
    logger.info('{func:s}: RINEX observation file {obs:s} accessible'.format(func=cFuncName, obs=colored('{!s}'.format(amc.dRTK['args']['obs_name']), 'green')))


def main(argv):
    """
    creates a combined SBF file from hourly or six-hourly SBF files
    """
    amc.cBaseName = colored(os.path.basename(__file__), 'yellow')
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    obsRnx, dirRnx, obs_types, sat_systs, frequencies, prns, interval, logLevels = treatCmdOpts(argv)

    # store cli parameters
    amc.dRTK = {}
    dInfo = {}
    amc.dRTK['info'] = dInfo

    dArgs = {}
    dArgs['dir'] = dirRnx
    dArgs['obs_name'] = obsRnx
    dArgs['gnss'] = sat_systs
    dArgs['systyp'] = obs_types
    dArgs['sysfrq'] = frequencies
    dArgs['prns'] = prns
    dArgs['interval'] = interval

    amc.dRTK['args'] = dArgs

    # create logging for better debugging
    logger = amc.createLoggers(os.path.basename(__file__), dir=dirRnx, logLevels=logLevels)
    # locate the gfzrnx program used for execution
    dProgs = {}
    dProgs['gfzrnx'] = location.locateProg('gfzrnx', logger)
    dProgs['grep'] = location.locateProg('grep', logger)
    amc.dRTK['progs'] = dProgs

    # check arguments
    checkArguments(logger=logger)

    # read the header info using gfzrnx
    amc.dRTK['info']['header'] = rnx_obs_header.rnxobs_header_metadata(dArgs=amc.dRTK['args'], dProgs=amc.dRTK['progs'], logger=logger)
    # get list of PRNs in RINEX obs file
    amc.dRTK['info']['prns'] = rnx_obs_header.rnxobs_parse_prns(dArgs=amc.dRTK['args'], dProgs=amc.dRTK['progs'], logger=logger)
    # extract parts of the rinex observation header
    amc.dRTK['available'] = rnx_obs_header.rnxobs_metadata_parser(dobs_hdr=amc.dRTK['info']['header'], dPRNs=amc.dRTK['info']['prns'], dArgs=amc.dRTK['args'], logger=logger)
    amc.dRTK['analysed'] = rnx_obs_header.rnxobs_argument_parser(dobs_hdr=amc.dRTK['info']['header'], dPRNs=amc.dRTK['info']['prns'], dArgs=amc.dRTK['args'], logger=logger)

    # for each PRN selected, extract the variables of same systyp in tabular output and read in a dataframe
    for gnss in amc.dRTK['analysed']:
        logger.info('=' * 50)
        logger.info('{func:s}: start analysing GNSS {gnss:s}'.format(gnss=colored(gnss, 'green'), func=cFuncName))

        for prn in amc.dRTK['analysed'][gnss]['prns']:
            logger.info('-' * 25)
            # create a dataframe from the rinex observation file
            dfPRN = rnx_obs_analyse.rnxobs_dataframe(rnx_file=dArgs['obs_name'], prn=prn, dPRNObs=amc.dRTK['analysed'][gnss]['sysobs'], dProgs=amc.dRTK['progs'], logger=logger)

            # perform analysis calculations
            rnx_obs_analyse.rnxobs_analyse(prn=prn, dfPrn=dfPRN, dPRNObs=amc.dRTK['analysed'][gnss]['systyp'], logger=logger)

    # show the information JSON structure
    logger.info('{func:s}: info dictionary = \n{prt!s}'.format(prt=amutils.pretty(amc.dRTK), func=cFuncName))

if __name__ == "__main__":
    main(sys.argv)
