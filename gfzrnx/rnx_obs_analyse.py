import os
import sys
import logging
from termcolor import colored
import numpy as np
import pandas as pd
import uuid
from datetime import datetime

import am_config as amc
from ampyutils import  exeprogram, amutils
from GNSS import gpstime


def datetime_from_date_time(date: str, time:str) -> datetime:
    """
    datetime_from_date_time converts drom date and time given in strings to a datetime python structure
    """
    datetime_str = '{date:s} {hms:s}'.format(date=date, hms=time[:-1])
    print('DT = {!s}'.format(datetime_str))
    print('DT = {!s}'.format(type(datetime_str)))

    try:
        datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as ve:
        print('ValueError Raised:', ve)

    return datetime_object


def rnxobs_dataframe(rnx_file: str, prn: str, dPRNSysObs: dict, dProgs:dict, logger: logging.Logger) -> dict:
    """
    rnxobs_dataframe selects the observations for a PRN and returns observation dataframe
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('{func:s}: creating dataframe for PRN {prn:s} with observations {obs:s}'.format(prn=prn, obs=', '.join(dPRNSysObs), func=cFuncName))

    # create tabular output for this PRN
    tab_name = '/tmp/{tmpname:s}.tab'.format(tmpname=uuid.uuid4().hex)

    cmdGFZRNX = '{prog:s} -finp {rnx:s} -fout {out:s} -tab_obs -tab_sep "," -prn {prn:s} -obs_types={obs:s}'.format(prog=dProgs['gfzrnx'], rnx=rnx_file, out=tab_name, prn=prn, obs=','.join(dPRNSysObs))

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
    # add datetime columns
    # dfPos['DT'] = dfPrn.apply(lambda x: gpstime.UTCFromWT(x['WNC'], x['TOW']), axis=1)
    # datetime_str = '09/19/18 13:55:26'
    date_time_str = '2018-06-29 08:15:27.243860'
    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

    print('DT = {!s}'.format(date_time_str))
    print('DT = {!s}'.format(type(date_time_str)))
    print('Date:', date_time_obj.date())
    print('Time:', date_time_obj.time())
    print('Date-time:', date_time_obj)

    datetime_str = '{date:s} {hms:s}'.format(date=dfPrn['DATE'][0], hms=dfPrn['TIME'][0][:-1])
    print('DT = {!s}'.format(datetime_str))
    print('DT = {!s}'.format(type(datetime_str)))

    try:
        datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as ve:
        print('ValueError Raised:', ve)

    print('DT = {!s}'.format(datetime_object))
    print('DT = {!s}'.format(type(datetime_object)))

    datetime_str = '{date:s} {hms:s}'.format(date=dfPrn['DATE'][76], hms=dfPrn['TIME'][76][:-1])
    datetime_object = datetime_from_date_time(date=dfPrn['DATE'][76], time=dfPrn['TIME'][76])
    print('DT = {!s}'.format(datetime_object))
    print('DT = {!s}'.format(type(datetime_object)))


    amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=dfPrn, dfName='{tab:s}'.format(tab='{prn:s} with observables = {obs!s}'.format(prn=prn, obs=', '.join(dPRNSysObs))))

    # remove the temporary tabular file
    os.remove(tab_name)

    return dfPrn


def rnxobs_analyse(prn: str, dfPrn: pd.DataFrame, dPRNSysType: dict, logger: logging.Logger):
    """
    rnxobs_analyse calculates differences between similar observations
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('\n')
    logger.info('{func:s}: analysing PRN {prn:s} observations {obs:s}'.format(prn=prn, obs=', '.join(dPRNSysType), func=cFuncName))

    # check for this PRN which observation types it has by checking the dataframe column names
    col_observables = list(dfPrn)[5:]
    logger.info('{func:s}: PRN {prn:s} has observables {obs:s}'.format(prn=prn, obs=', '.join(col_observables), func=cFuncName))

    for _, sigtyp in enumerate(dPRNSysType):
        # check whether for this PRN we have the current signal type (C,S,D,L)
        # print('sigtype = {!s}'.format(sigtyp))
        prn_sigtyps = [prn_sigtyp for prn_sigtyp in col_observables if prn_sigtyp[0] == sigtyp]

        # create col names for the possible differences
        for i in range(len(prn_sigtyps)-1):
            for j in range(i+1, len(prn_sigtyps)):
                new_col = '{st1:s}-{st2:s}'.format(st1=prn_sigtyps[i], st2=prn_sigtyps[j])
                # print('{:d} {:d} newcol = {:s}'.format(i, j, new_col))

                dfPrn[new_col] = dfPrn[prn_sigtyps[i]].sub(dfPrn[prn_sigtyps[j]])

                # print(dfPrn[prn_sigtyps[i]].describe())
                # print(dfPrn[prn_sigtyps[j]].describe())
                # print(dfPrn[new_col].describe())

    amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=dfPrn, dfName='{tab:s}'.format(tab='{prn:s} with observables = {obs!s}'.format(prn=prn, obs=', '.join(dPRNSysType))))

    # df1['Score_diff'] = df1['score1'].sub(df1['score2'], axis = 0)
    # dfPrn

