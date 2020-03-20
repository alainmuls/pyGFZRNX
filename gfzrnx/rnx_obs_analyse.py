import os
import sys
import logging
from termcolor import colored

import am_config as amc
from ampyutils import  exeprogram, amutils


def rnxobs_prn_obs(prn: str, dAnalyse: dict, dProgs:dict, logger: logging.Logger) -> dict:
    """
    rnxobs_header_metadata reads the rinex observation file header and extracts info
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    print('sysobs = {!s}'.format(dAnalyse['sysobs']))


    pass

