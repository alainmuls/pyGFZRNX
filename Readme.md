# Python scripts for RINEX examination

## Overview

Python scripts in this environment have been developed using the open source program [gfzrnx](http://dataservices.gfz-potsdam.de/panmetaworks/showshort.php?id=escidoc:1577894), _RINEX GNSS Data Conversion and Manipulation Toolbox_,  a software toolbox for Global Navigation Satellite System (GNSS) data provided in the REceiver Independent EXchange format (RINEX) of the major versions 2 and 3.

The following RINEX data types are supported:

- Observation data
- Navigation data
- Meteorological data

The following global and regional satellite systems are supported:

- GPS - Global Positioning System (USA)
- GLONASS - GLObal NAvigation Satellite System (RUS)
- BEIDOU - Chinese Global and Regional Navigation Satellite System (CHN)
- GALILEO - European Global Navigation Satellite System
- IRNSS - Indian Regional Naviagation Satellite System (IND)
- QZSS - Quasi Zenith Satellite System (JAP)

The following operations/tasks are supported:

- RINEX data check and repair
- RINEX data format conversion ( version 3 to 2 and vice versa )
- RINEX data splice
- RINEX data split
- RINEX data statistics generation
- RINEX data manipulations like: (1) data sampling, (2) observation types selection, (3) satellite systems selection, (4) elimination of overall empty or sparse observation types
- Automatic version dependent file naming on output data
- RINEX data header editing
- RINEX data meta data extraction
- RINEX data comparison

Following scripts have been developed:

- __`pyrnxobsinfo.py`__ scans the RINEX observation header and reports information what is available in the RINEX observation file under investigation.
- __`pygfzrnx.py`__ plots selected observables for selected GNSS and PRNs as well as differences between similar observation types.

## Script `pyrnxobsinfo.py`

\scriptsize

```bash
[amuls:~/amPython/pyGFZRNX] [pyGFZRNX] $ pyrnxobsinfo.py --help
usage: pyrnxobsinfo.py [-h] -r OBSRNX [-d DIRRNX] [-i INTERVAL]
                       [-l LOGGING LOGGING]

pyrnxobsinfo.py reads RINEX observation files and lists available information

optional arguments:
  -h, --help            show this help message and exit
  -r OBSRNX, --obsRnx OBSRNX
                        rinex observation file
  -d DIRRNX, --dirRnx DIRRNX
                        Directory of SBF file (default ./)
  -i INTERVAL, --interval INTERVAL
                        interval in sec for scanning observation file (default
                        600 s)
  -l LOGGING LOGGING, --logging LOGGING LOGGING
                        specify logging level console/file (default INFO
                        DEBUG)
```

\normalsize

The following information, logged in file `pyrnxobsinfo.log`, is returned by `pyrnxobsinfo.py`:

\tiny

```bash
INFO: location.py - locateProg: locate programs gfzrnx
INFO: location.py - locateProg: gfzrnx is /home/amuls/bin/gfzrnx
INFO: location.py - locateProg: locate programs grep
INFO: location.py - locateProg: grep is /bin/grep
INFO: pyrnxobsinfo.py - checkArguments: working directory is /home/amuls/amPython/pyGFZRNX/data
INFO: pyrnxobsinfo.py - checkArguments: changed to directory /home/amuls/amPython/pyGFZRNX/data
INFO: pyrnxobsinfo.py - checkArguments: RINEX observation file P1710171.20O accessible
INFO: rnx_obs_header.py - rnxobs_header_metadata: Running:
/home/amuls/bin/gfzrnx -meta basic:jsonp -finp P1710171.20O -fout /tmp/P1710171_20O.json
INFO: rnx_obs_header.py - rnxobs_parse_prns: Running:
/home/amuls/bin/gfzrnx -stk_epo 300 -finp P1710171.20O -fout /tmp/P1710171_20O.prns
INFO: {func:s}: display of observation time span
INFO: 
INFO:  STT 20200117 06:00   06:40   07:20   08:00   08:40   09:20   10:00   10:40   11:20   12:00   
INFO:  STH            +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
INFO:  STE SEPT E E01 |   |*********************************************************  |   |   | E01
INFO:  STE SEPT E E03 |   |   |   |   |   |   |   |   |   |   |  *****************************| E03
INFO:  STE SEPT E E04 **********************************************************  |   |   |   | E04
INFO:  STE SEPT E E05 |   |   | **************************************************************| E05
INFO:  STE SEPT E E09 ************************************************************************| E09
INFO:  STE SEPT E E11 ************************************|   |   |   |   |   |   |   |   |   | E11
INFO:  STE SEPT E E12 **************  |   |   |   |   |   |   |   |   |   |   |   |   |   |   | E12
INFO:  STE SEPT E E13 |   |   |   |   |   |   |   |   |   |   |   |   |   |*******************| E13
INFO:  STE SEPT E E14 ******************************* |   |   |   |   |   |   |   |   |   |   | E14
INFO:  STE SEPT E E15 |   |   |   |   |   |   |   |*******************************************| E15
INFO:  STE SEPT E E19 *********************   |   |   |   |   |   |   |   |   |   |   |   |   | E19
INFO:  STE SEPT E E21 ****************************************|   |   |   |   |   |   |   |   | E21
INFO:  STE SEPT E E24 |   |   |   |   |   |   |   |   | **************************************| E24
INFO:  STE SEPT E E25 |   |   |   |   |   |   |   |   |   |   |   |   |   |   ****************| E25
INFO:  STE SEPT E E27 ****************|   |   |   |   |   |   |   |   |   |   |   |   |   |   | E27
INFO:  STS            |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
INFO:  STE SEPT G G01 *************   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | G01
INFO:  STE SEPT G G02 |   *********************************************************** |   |   | G02
INFO:  STE SEPT G G03 **********************************  |   |   |   |   |   |   |   |   |   | G03
INFO:  STE SEPT G G04 *********************************************** |   |   |   |   |   |   | G04
INFO:  STE SEPT G G05 |   |   |   |   |   | **************************************************| G05
INFO:  STE SEPT G G06 *****************************************************   |   |   |   |   | G06
INFO:  STE SEPT G G07 |   |   |***************************************************************| G07
INFO:  STE SEPT G G08 |   |   |   |   |   |   |   |   |   |   |   |   |   |   ****************| G08
INFO:  STE SEPT G G09 *************************************************************** |   |   | G09
INFO:  STE SEPT G G11 **  |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | G11
INFO:  STE SEPT G G12 |****   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | G12
INFO:  STE SEPT G G13 |   |   |   |   |   |   |   |   |  *************************************| G13
INFO:  STE SEPT G G15 |   |   |   |   |   |   |   |   |   |   |   |   | **********************| G15
INFO:  STE SEPT G G16 |   |   |   |   |***********************************|   |   |   |   |   | G16
INFO:  STE SEPT G G17 ********************|   |   |   |   |   |   |   |   |   |   |   |   |   | G17
INFO:  STE SEPT G G19 **************************  |   |   |   |   |   |   |   |   |   |   |   | G19
INFO:  STE SEPT G G20 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |***| G20
INFO:  STE SEPT G G21 |   |   |   |   |   |   |   |   |   |   |   |   | **********************| G21
INFO:  STE SEPT G G22 *********************** |   |   |   |   |   |   |   |   |   |   |   |   | G22
INFO:  STE SEPT G G23 **************************************************  |   |   |   |   |   | G23
INFO:  STE SEPT G G24 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  *| G24
INFO:  STE SEPT G G25 | ********  |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | G25
INFO:  STE SEPT G G26 |   |   |   ****************************|   |   |   |   |   |   |   |   | G26
INFO:  STE SEPT G G27 |   |   |   |   |   |   |   |   |   |   |   |   |  ****** **************| G27
INFO:  STE SEPT G G28 |   |   |   |   |   |   |   |   |   |   |   |  *************************| G28
INFO:  STE SEPT G G29 |   |   |   |   |   |   |************************   |   |   |   |   |   | G29
INFO:  STE SEPT G G30 |   |   |   |   |   ****************************************************| G30
INFO:  STE SEPT G G31 *****************   |   |   |   |   |   |   |   |   |   |   |   |   |   | G31
INFO:  STH            +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
INFO:  STT 20200117 06:00   06:40   07:20   08:00   08:40   09:20   10:00   10:40   11:20   12:00   
INFO: rnx_obs_header.py - rnxobs_parse_prns: list of PRNs with observations
   E01, E03, E04, E05, E09, E11, E12, E13, E14, E15, E19, E21, E24, E25, E27, G01, G02, G03, G04, G05, G06, G07, G08, G09, G11, G12, G13, G15, G16, G17, G19, G20, G21, G22, G23, G24, G25, G26, G27, G28, G29, G30, G31
INFO: rnx_obs_header.py - rnxobs_metadata_parser: Available 
   GNSS: G
      frequencies: 1, 2, 5
      observation types: C, D, L, S
      observation codes: C1C, C1W, C2L, C2W, C5Q, D1C, D2L, D2W, D5Q, L1C, L2L, L2W, L5Q, S1C, S1W, S2L, S2W, S5Q
      PRNs (#28): G01, G02, G03, G04, G05, G06, G07, G08, G09, G11, G12, G13, G15, G16, G17, G19, G20, G21, G22, G23, G24, G25, G26, G27, G28, G29, G30, G31
INFO: rnx_obs_header.py - rnxobs_metadata_parser: Available 
   GNSS: E
      frequencies: 1, 5
      observation types: C, D, L, S
      observation codes: C1C, C5Q, D1C, D5Q, L1C, L5Q, S1C, S5Q
      PRNs (#15): E01, E03, E04, E05, E09, E11, E12, E13, E14, E15, E19, E21, E24, E25, E27
INFO: pyrnxobsinfo.py - main: info dictionary = 
{
    'info': {
        'header': {
            'antenna': {
                'height': {
                    'e': 0,
                    'h': 0,
                    'n': 0
                },
                'name': 'Unknown',
                'number': 'Unknown',
                'radome': 'NONE'
            },
            'data': {
                'epoch': {
                    'first': '2020 01 17 06 00 00.0000000',
                    'last': '2020 01 17 11 59 59.0000000'
                }
            },
            'exec': {
                'date': '2020-03-23 09:48:39 UTC',
                'meta': 'basic',
                'name': 'gfzrnx',
                'version': '1.12-7747'
            },
            'file': {
                'duration': '86400',
                'epo_first': '2020 01 17 06 00 00.0000000',
                'epo_first_name': '2020 01 17 00 00 00.0000000',
                'interval': '1.000',
                'md5': '1d24cfe740065f076796822841d13087',
                'name': 'P1710171.20O',
                'pgm': 'sbf2rin-13.4.3',
                'pgm_date': '20200317 143355 UTC',
                'pgm_runby': '',
                'satsys': 'GE',
                'site': 'P171',
                'source': 'R',
                'sysfrq': {
                    'E': [
                        '1',
                        '5'
                    ],
                    'G': [
                        '1',
                        '2',
                        '5'
                    ]
                },
                'sysobs': {
                    'E': [
                        'C1C',
                        'C5Q',
                        'D1C',
                        'D5Q',
                        'L1C',
                        'L5Q',
                        'S1C',
                        'S5Q'
                    ],
                    'G': [
                        'C1C',
                        'C1W',
                        'C2L',
                        'C2W',
                        'C5Q',
                        'D1C',
                        'D2L',
                        'D2W',
                        'D5Q',
                        'L1C',
                        'L2L',
                        'L2W',
                        'L5Q',
                        'S1C',
                        'S1W',
                        'S2L',
                        'S2W',
                        'S5Q'
                    ]
                },
                'system': 'M',
                'systyp': {
                    'E': [
                        'C',
                        'D',
                        'L',
                        'S'
                    ],
                    'G': [
                        'C',
                        'D',
                        'L',
                        'S'
                    ]
                },
                'type': 'O',
                'version': '3.04'
            },
            'receiver': {
                'firmware': '2.3.4',
                'name': 'SEPT ASTERX3',
                'number': '3000221'
            },
            'site': {
                'agency': 'Unknown',
                'name': 'P171',
                'number': 'Unknown',
                'observer': 'Unknown',
                'position': {
                    'x': '4023741.4621',
                    'y': '309110.9488',
                    'z': '4922723.5932'
                }
            }
        },
        'prns': [
            'E01',
            'E03',
            'E04',
            'E05',
            'E09',
            'E11',
            'E12',
            'E13',
            'E14',
            'E15',
            'E19',
            'E21',
            'E24',
            'E25',
            'E27',
            'G01',
            'G02',
            'G03',
            'G04',
            'G05',
            'G06',
            'G07',
            'G08',
            'G09',
            'G11',
            'G12',
            'G13',
            'G15',
            'G16',
            'G17',
            'G19',
            'G20',
            'G21',
            'G22',
            'G23',
            'G24',
            'G25',
            'G26',
            'G27',
            'G28',
            'G29',
            'G30',
            'G31'
        ]
    },
    'args': {
        'dir': '/home/amuls/amPython/pyGFZRNX/data/',
        'obs_name': 'P1710171.20O'
    },
    'progs': {
        'gfzrnx': '/home/amuls/bin/gfzrnx',
        'grep': '/bin/grep'
    }
}
```

\normalsize
