import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys
from termcolor import colored
import logging

from ampyutils import amutils

__author__ = 'amuls'


def rnx_prsobs_plot(dArgs: dict, prn: str, stobs: list, dfPrn: pd.DataFrame, rawobs: list, logger: logging.Logger, showplot: bool = False):
    """
    rnx_prsobs_plot plots the observations for PRN contained in dfPRN for a specific systyp
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # deterimine text for the sigtyp plotted
    if stobs[0][0] == 'C':
        str_obs = 'Pseudo Range [m]'
    elif stobs[0][0] == 'S':
        str_obs = 'Signal strength [dbHz]'
    elif stobs[0][0] == 'L':
        str_obs = 'Carrier waves [-]'
    elif stobs[0][0] == 'D':
        str_obs = 'Doppler frequency [Hz]'

    # set up the plot
    plt.style.use('ggplot')

    # determine the discrete colors for all observables
    colormap = plt.cm.tab20  # I suggest to use nipy_spectral, Set1, Paired
    colors = [colormap(i) for i in np.linspace(0, 1, len(stobs) * 2)]
    # print('colors = {!s}'.format(colors))

    fig, ax = plt.subplots(figsize=(18.0, 12.0))

    # print the raw observables on first y axis
    count = 0
    lstlabels = []  # store the label info
    for i, obs in enumerate([obs for obs in stobs if obs in rawobs]):
        txt_label = ax.plot(dfPrn['DT'], dfPrn[obs], color=colors[i], marker='.', linestyle='-', markersize=3, label=obs, alpha=max(0.9 - 0.075 * i, 0.25))
        lstlabels += txt_label
        count += 1

    ax.set_ylabel('Signal Type:  {:s}'.format(str_obs), fontsize='large')
    ax.set_xlabel('Date time', fontsize='large')

    # print the difference in observables on second y axis
    ax2 = ax.twinx()
    for j, obs in enumerate([obs for obs in stobs if obs not in rawobs]):
        txt_label = ax2.plot(dfPrn['DT'], dfPrn[obs], color=colors[count + j], marker='x', linestyle='-', markersize=3, label=obs, alpha=max(0.9 - 0.075 * j, 0.25))
        lstlabels += txt_label

    ax2.set_ylabel('Difference of Signal Type: {:s}'.format(str_obs), fontsize='large')

    # show combined label information
    labs = [l.get_label() for l in lstlabels]
    ax.legend(lstlabels, labs, loc='upper center', bbox_to_anchor=(0.5, 1.025), ncol=10, fancybox=True, shadow=True, facecolor='white', framealpha=1, fontsize='large', markerscale=6)
    # # get the individual lines inside legend and set line width
    # leg = ax.legend()
    # for line in leg.get_lines():
    #     line.set_linewidth(4)
    # # get label texts inside legend and set font size
    # for text in leg.get_texts():
    #     text.set_fontsize('x-large')

    # set the title of plot
    fig.suptitle('File: {name:s} | PRN: {prn:s} | Type: {obs:s}'.format(name=dArgs['obs_name'], obs=str_obs, prn=prn), fontsize='x-large')

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    pngName = os.path.join('png', '{name:s}-{prn:s}-{obs:s}.png'.format(name=dArgs['obs_name'].replace('.', '-'), prn=prn, obs=stobs[0][0]))
    fig.savefig(pngName, dpi=fig.dpi)

    logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(pngName, 'green')))

    if showplot:
        plt.show(block=True)
    else:
        plt.close(fig)
