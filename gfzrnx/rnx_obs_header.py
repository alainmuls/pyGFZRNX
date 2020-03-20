import os
import sys
import logging
from termcolor import colored
import json

import am_config as amc
from ampyutils import  exeprogram, amutils


def rnxobs_header_metadata(dArgs: dict, dProgs:dict, logger: logging.Logger) -> dict:
    """
    rnxobs_header_metadata reads the rinex observation file header and extracts info
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # extract the header meta data into a json structure
    cmdGFZRNX = '{prog:s} -meta basic:jsonp -finp {obs:s} -fout /tmp/{obs:s}.json'.format(prog=dProgs['gfzrnx'], obs=dArgs['obs_name'])
    print('cmdGFZRNX = {!s}'.format(cmdGFZRNX))
    logger.info('{func:s}: Running:\n{cmd:s}'.format(func=cFuncName, cmd=colored(cmdGFZRNX, 'blue')))

    # run the program
    # gfzrnx -finp data/P1710171.20O -meta basic:jsonp
    exeprogram.subProcessDisplayStdErr(cmd=cmdGFZRNX, verbose=False)

    with open('/tmp/{obs:s}.json'.format(obs=dArgs['obs_name'])) as json_file:
        hdr_obs = json.load(json_file)

    return hdr_obs


def rnxobs_metadata_parser(dobs_hdr: dict, dArgs: dict, logger: logging.Logger) -> dict:
    """
    rnxobs_metadata_parser parser useful info from the header and stores in dictionary
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # dictionary containing relevant info
    drnx_obs = {}

    # get the GNSSs cavailable
    rnx_info = []
    GNSSs = list(dobs_hdr['file']['satsys'])
    for gnss in GNSSs:
        # create info text to inform user what is available
        txt_info = '\n   GNSS: {gnss:s}'.format(gnss=gnss)
        txt_info += '\n      frequencies: {freq!s}'.format(gnss=gnss, freq=', '.join(dobs_hdr['file']['sysfrq'][gnss]))
        txt_info += '\n      observation types: {type!s}'.format(type=', '.join(dobs_hdr['file']['systyp'][gnss]))
        txt_info += '\n      observation codes: {obs!s}'.format(obs=', '.join(dobs_hdr['file']['sysobs'][gnss]))
        logger.info('{func:s}: Available {info:s}'.format(info=txt_info, func=cFuncName))

        if gnss in dArgs['gnss']:
            drnx_obs[gnss] = {}

            # get the frequencies for this GNSS
            drnx_obs[gnss]['sysfrq'] = [freq for freq in dobs_hdr['file']['sysfrq'][gnss] if freq in dArgs['sysfrq']]
            # get the observation types for this GNSS
            drnx_obs[gnss]['systyp'] = [systyp for systyp in dobs_hdr['file']['systyp'][gnss] if systyp in dArgs['systyp']]

            # get the observation codes for this GNSS
            drnx_obs[gnss]['sysobs'] = [sysobs for sysobs in dobs_hdr['file']['sysobs'][gnss] if sysobs[0] in dArgs['systyp']]

            # create list of possible PRNs for this GNSS
            print(dArgs['prns'])
            print(type(dArgs['prns']))
            drnx_obs[gnss]['prns'] = ['{gnss:s}{prn:02d}'.format(gnss=gnss, prn=prn) for prn in range(1, 37) if prn in dArgs['prns'] ]

            # create info text to inform user what is available
            txt_exam  = '\n   GNSS: {gnss:s}'.format(gnss=gnss)
            txt_exam += '\n      frequencies: {freq!s}'.format(freq=', '.join(drnx_obs[gnss]['sysfrq']))
            txt_exam += '\n      observation codes: {obs!s}'.format(obs=', '.join(drnx_obs[gnss]['sysobs']))
            txt_exam += '\n      PRNs: {prns!s}'.format(prns=', '.join(drnx_obs[gnss]['prns']))
            logger.info('{func:s}: Analysed {info:s}'.format(info=txt_exam, func=cFuncName))

    logger.info('{func:s}: observables to analyse\n{analyse!s}'.format(analyse=amutils.pretty(drnx_obs), func=cFuncName))

    return drnx_obs
