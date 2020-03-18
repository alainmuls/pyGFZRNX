import os
import sys
import logging
from termcolor import colored


def rnxobs_header_metadata(dRnx: dict, dProgs:dict, logger: logging.Logger):
    """
    rnxobs_header_metadata reads the rinex observation file header and extracts info
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # extract the header meta data into a json structure
    cmdGFZRNX = '{prog:s} -meta basic:jsonp -finp {obs:s} -fout /tmp/{obs:s}.json'.format(prog=dProgs['gfzrnx'], obs=dRnx['obs'])

    print('cmdGFZRNX = {!s}'.format(cmdGFZRNX))

    # gfzrnx -finp data/P1710171.20O -meta basic:jsonp
