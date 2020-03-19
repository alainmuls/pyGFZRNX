import os
import sys
import logging
from termcolor import colored
import json

import am_config as amc
from ampyutils import  exeprogram


def rnxobs_header_metadata(dRnx: dict, dProgs:dict, logger: logging.Logger) -> dict:
    """
    rnxobs_header_metadata reads the rinex observation file header and extracts info
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # extract the header meta data into a json structure
    cmdGFZRNX = '{prog:s} -meta basic:jsonp -finp {obs:s} -fout /tmp/{obs:s}.json'.format(prog=dProgs['gfzrnx'], obs=dRnx['obs_name'])
    print('cmdGFZRNX = {!s}'.format(cmdGFZRNX))
    logger.info('{func:s}: Running:\n{cmd:s}'.format(func=cFuncName, cmd=colored(cmdGFZRNX, 'blue')))

    # run the program
    # gfzrnx -finp data/P1710171.20O -meta basic:jsonp
    exeprogram.subProcessDisplayStdErr(cmd=cmdGFZRNX, verbose=False)

    with open('/tmp/{obs:s}.json'.format(obs=dRnx['obs_name'])) as json_file:
        hdr_obs = json.load(json_file)

    print(type(hdr_obs))
    print(hdr_obs)

    return hdr_obs
