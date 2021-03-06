import os
import sys
import logging
from termcolor import colored
import json
import uuid
import tempfile

from ampyutils import exeprogram, amutils


def rnxobs_header_metadata(dArgs: dict, dProgs: dict, logger: logging.Logger) -> dict:
    """
    rnxobs_header_metadata reads the rinex observation file header and extracts info
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # extract the header meta data into a json structure
    json_name = os.path.join(tempfile.gettempdir(), '{tmpname:s}.json'.format(tmpname=uuid.uuid4().hex))

    cmdGFZRNX = '{prog:s} -meta basic:jsonp -finp {obs:s} -fout {json:s}'.format(prog=dProgs['gfzrnx'], obs=dArgs['obs_name'], json=json_name)
    logger.info('{func:s}: Running:\n{cmd:s}'.format(func=cFuncName, cmd=colored(cmdGFZRNX, 'blue')))

    # run the program
    # gfzrnx -finp data/P1710171.20O -meta basic:jsonp
    exeprogram.subProcessDisplayStdErr(cmd=cmdGFZRNX, verbose=False)

    with open(json_name) as json_file:
        hdr_obs = json.load(json_file)

    # remove the temporary json file
    os.remove(json_name)

    return hdr_obs


def rnxobs_parse_prns(dArgs: dict, dProgs: dict, logger: logging.Logger) -> list:
    """
    rnxobs_parse_prns gets th elist of PRNs in observation file
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    prns_name = os.path.join(tempfile.gettempdir(), '{tmpname:s}.prns'.format(tmpname=uuid.uuid4().hex))

    cmdGFZRNX = '{prog:s} -stk_epo {interval:d} -finp {obs:s} -fout {prns:s}'.format(prog=dProgs['gfzrnx'], interval=dArgs['interval'], obs=dArgs['obs_name'], prns=prns_name)
    logger.info('{func:s}: Running:\n{cmd:s}'.format(func=cFuncName, cmd=colored(cmdGFZRNX, 'blue')))

    # run the program
    # gfzrnx -stk_epo 300-finp data/P1710171.20O
    exeprogram.subProcessDisplayStdErr(cmd=cmdGFZRNX, verbose=False)

    # extract the PRNs which are last elements in lines starting with STE
    lstPRNS = []
    logger.info('{func:s}: display of observation time span'.format(func=cFuncName))
    with open(prns_name) as f:
        for line in f:
            # print('{line:s} -- {STE!s}'.format(line=line, STE=line.startswith(' STE')))
            if line.startswith(' STE'):
                lstPRNS.append(line.split('|')[-1].strip())
            logger.info(line[:-1])

    logger.info('{func:s}: list of PRNs with observations\n   {prns!s}'.format(prns=', '.join(lstPRNS), func=cFuncName))

    # remove the temporary json file
    os.remove(prns_name)

    return lstPRNS


def rnxobs_metadata_parser(dobs_hdr: dict, dPRNs: dict, dArgs: dict, logger: logging.Logger):
    """
    rnxobs_metadata_parser parser useful info from the header and stores in dictionary
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # get the GNSSs cavailable
    GNSSs = list(dobs_hdr['file']['satsys'])
    for gnss in GNSSs:
        # create info text to inform user what is available
        txt_info = '\n   GNSS: {gnss:s}'.format(gnss=gnss)
        txt_info += '\n      frequencies: {freq!s}'.format(gnss=gnss, freq=', '.join(dobs_hdr['file']['sysfrq'][gnss]))
        txt_info += '\n      observation types: {type!s}'.format(type=', '.join(dobs_hdr['file']['systyp'][gnss]))
        txt_info += '\n      observation codes: {obs!s}'.format(obs=', '.join(dobs_hdr['file']['sysobs'][gnss]))
        gnss_prns = [prn for prn in dPRNs if prn[0] == gnss]
        txt_info += '\n      PRNs (#{nbr:d}): {prns!s}'.format(prns=', '.join(gnss_prns), nbr=len(gnss_prns))
        logger.info('{func:s}: Available {info:s}'.format(info=txt_info, func=cFuncName))


def rnxobs_argument_parser(dobs_hdr: dict, dPRNs: dict, dArgs: dict, logger: logging.Logger) -> dict:
    """
    rnxobs_metadata_parser parser useful info from the header and stores in dictionary
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # dictionary containing relevant info
    drnx_obs = {}

    # get the GNSSs cavailable
    GNSSs = list(dobs_hdr['file']['satsys'])
    for gnss in GNSSs:
        if gnss in dArgs['gnss']:
            drnx_obs[gnss] = {}

            # get the frequencies for this GNSS
            # drnx_obs[gnss]['sysfrq'] = [freq for freq in dobs_hdr['file']['sysfrq'][gnss] if freq in dArgs['sysfrq']]
            # get the observation types for this GNSS
            drnx_obs[gnss]['systyp'] = [systyp for systyp in dobs_hdr['file']['systyp'][gnss] if systyp in dArgs['systyp']]

            # get the observation codes for this GNSS
            drnx_obs[gnss]['sysobs'] = [sysobs for sysobs in dobs_hdr['file']['sysobs'][gnss] if sysobs[0] in dArgs['systyp'] and sysobs[1] in dArgs['sysfrq']]

            # create list of available PRNs with observables for this GNSS
            prns_asked = ['{gnss:s}{prn:02d}'.format(gnss=gnss, prn=prn) for prn in range(1, 37) if prn in dArgs['prns']]
            drnx_obs[gnss]['prns'] = [prn for prn in prns_asked if prn in dPRNs]

            # create info text to inform user what is available
            txt_exam = '\n   GNSS: {gnss:s}'.format(gnss=gnss)
            # txt_exam += '\n      frequencies: {freq!s}'.format(freq=', '.join(drnx_obs[gnss]['sysfrq']))
            txt_exam += '\n      observation codes: {obs!s}'.format(obs=', '.join(drnx_obs[gnss]['sysobs']))
            txt_exam += '\n      PRNs: {prns!s}'.format(prns=', '.join(drnx_obs[gnss]['prns']))
            logger.info('{func:s}: Analysed {info:s}'.format(info=txt_exam, func=cFuncName))

    logger.info('{func:s}: observables to analyse\n{analyse!s}'.format(analyse=amutils.pretty(drnx_obs), func=cFuncName))

    return drnx_obs
