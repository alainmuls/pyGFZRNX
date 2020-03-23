import os
import sys
import logging
from termcolor import colored
import numpy as np
import pandas as pd
import uuid

import am_config as amc
from ampyutils import  exeprogram, amutils


def rnxobs_prn_obs(rnx_file: str, prn: str, dPRNObs: dict, dProgs:dict, logger: logging.Logger) -> dict:
    """
    rnxobs_header_metadata reads the rinex observation file header and extracts info
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('{func:s}: analysing PRN {prn:s} observations {obs:s}'.format(prn=prn, obs=', '.join(dPRNObs), func=cFuncName))

    # create tabular output for this PRN
    tab_name = '/tmp/{tmpname:s}.tab'.format(tmpname=uuid.uuid4().hex)

    cmdGFZRNX = '{prog:s} -finp {rnx:s} -fout {out:s} -tab_obs -tab_sep "," -prn {prn:s} -obs_types={obs:s}'.format(prog=dProgs['gfzrnx'], rnx=rnx_file, out=tab_name, prn=prn, obs=','.join(dPRNObs))

    logger.info('{func:s}: Running:\n{prog:s}'.format(prog=colored(cmdGFZRNX, 'blue'), func=cFuncName))

    # run the program
    # gfzrnx -finp P1710171.20O -tab_obs -fout P1710171_20O.tab -prn E09 -obs_types C1C,C5Q -tab_sep ','
    exeprogram.subProcessDisplayStdErr(cmd=cmdGFZRNX, verbose=False)

    # find the header lines that don't belong to this GNSS system and remove that line
    hdlookup = '#HD,'
    gnsslookup = '#HD,{gnss:s}'.format(gnss=prn[0])

    hd_lines = []
    gnss_lines = []
    with open(tab_name) as f:
        for num, line in enumerate(f, 1):
            if hdlookup in line:
                # print('found at line: ', num)
                hd_lines.append(num)
            if gnsslookup in line:
                # print('found at line: ', num)
                gnss_lines.append(num)

    # print('hd_lines = {!s}'.format(hd_lines))
    # print('gnss_lines = {!s}'.format(gnss_lines))

    remove_lines = [linenr for linenr in hd_lines if linenr not in gnss_lines]
    # print('remove_lines = {!s}'.format(remove_lines))

    # remove the lines that are not related to current GNSS
    amutils.delete_lines(original_file=tab_name, lst_line_number=remove_lines)

    # read the CSV created file into a panda dataframe
    dfPrn = pd.read_csv(tab_name, delimiter = ',')
    amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=dfPrn, dfName='{tab:s}'.format(tab='{prn:s} with observables = {obs!s}'.format(prn=prn, obs=', '.join(dPRNObs))))

    # remove the temporary tabular file
    os.remove(tab_name)

    return dfPrn
