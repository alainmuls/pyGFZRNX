import os
import sys
import logging
from termcolor import colored

import am_config as amc
from ampyutils import  exeprogram, amutils


def rnxobs_prn_obs(rnx_file: str, prn: str, dPRNObs: dict, dProgs:dict, logger: logging.Logger) -> dict:
    """
    rnxobs_header_metadata reads the rinex observation file header and extracts info
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('{func:s}: analysing PRN {prn:s} observations {obs:s}'.format(prn=prn, obs=', '.join(dPRNObs), func=cFuncName))

    # create tabular output for this PRN
    file_tab = '/tmp/{rnx:s}.tab'.format(rnx=rnx_file.replace('.', '_'))
    cmdGFZRNX = '{prog:s} -finp {rnx:s} -fout {out:s} -tab_obs -tab_sep "," -prn {prn:s} -obs_types={obs:s}'.format(prog=dProgs['gfzrnx'], rnx=rnx_file, out=file_tab, prn=prn, obs=','.join(dPRNObs))

    print(cmdGFZRNX)

    # run the program
    # gfzrnx -finp P1710171.20O -tab_obs -fout P1710171_20O.tab -prn E09 -obs_types C1C,C5Q -tab_sep ','
    # exeprogram.subProcessDisplayStdErr(cmd=cmdGFZRNX, verbose=False)

    # remove the temporary json file
    os.remove(file_tab)

    pass
