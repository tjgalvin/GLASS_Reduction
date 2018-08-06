"""Utilities to help with the execution of miriad tasks and C3171 project data. 
"""
from glob import glob
import subprocess as sp
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymir as pymir
from pymir import mirstr as m
from astropy.time import Time
import astropy.units as u
import os
import sys
import shutil as su

# Get default logger set up in the reduction pipeline
import logging
logger = logging.getLogger()

# Added the mirstr as a package from github tjgalvin
# Hack until reduction scripts are updated
mirstr = pymir.mirstr

primary = '1934-638'
secondary = '0327-241'

flags_5 = {'chan_start':[None],
           'chan_end'  :[None]}

flags_9 = {'chan_start':[850],
           'chan_end'  :[900]}


frequencyFlagging = {
    # Known RFI ranges. taken from sensitivity calculator
    'rfi': [ [ 1059.0, 1075.0 ], [ 1103.0, 1117.0 ], [ 1145.0, 1159.0 ], [ 1165.0, 1191.0 ],
             [ 1217.0, 1239.0 ], [ 1240.0, 1252.0 ], [ 1380.0, 1382.0 ], [ 1428.0, 1432.0 ],
             [ 1436.0, 1450.0 ], [ 1456.0, 1460.0 ], [ 1493.0, 1495.0 ], [ 1499.0, 1511.0 ],
             [ 1525.0, 1628.0 ], [ 2489.0, 2496.0 ], [ 2879.0, 2881.0 ], [ 5622.0, 5628.0 ],
             [ 5930.0, 5960.0 ], [ 6440.0, 6480.0 ], [ 7747.0, 7777.0 ], [ 7866.0, 7896.0 ],
             [ 8058.0, 8088.0 ], [ 8177.0, 8207.0 ] ]
}
# -----------------------------------------------------------------------------
# Flagging utilities
# -----------------------------------------------------------------------------

def uvflag(vis, flag_def):
    """Flag the known bad channels from a visibility dataset.

    Stub function for the moment until channel ranges are made up
    
    Arguments:
        vis {str} -- Name of the visibility data to flag
        flag_def {dict} -- A dict with `chan_start` and `chan_end` channels to flag
    
    Raises:
        ValueError -- Raised if the `chan_start` and `chan_end` do not have same length
    """

    return
    if len(flag_def['chan_start']) != len(flag_def['chan_end']):
        raise ValueError('Chanels star and end should have the same length')
        
    for start, end in zip(flag_def['chan_start'], flag_def['chan_end']):
        line = f"chan,{end-start},{start},1"
        proc = mirstr(f"uvflag vis={vis} line={line} flagval=flag").run()
        logger.log(logging.INFO, proc)


def calibrator_pgflag(src):
    """A series of pgflag steps common to most (if not all) of
    the primary and secondary miriad uv files
    
    Arguments:
        src {str} -- The filename of the data to flag
    """
    # Automated flagging
    pgflag = m(f"pgflag vis={src} command='<b' stokes=i,q,u,v flagpar=8,5,5,3,6,3 options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<b' stokes=i,v,q,u flagpar=8,2,2,3,6,3  options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<b' stokes=i,v,u,q flagpar=8,2,2,3,6,3  options=nodisp").run()
    logger.log(logging.INFO, pgflag)


def mosaic_pgflag(src):
    """The name of the C3171 mosaic file to flag
    
    Arguments:
        src {str} -- Name of the file to flag
    """
    pgflag = m(f"pgflag vis={src} command='<b' stokes=i,v,q,u flagpar=8,2,2,3,6,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<b' stokes=i,v,u,q flagpar=8,2,2,3,6,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)


# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Source book keeping operations
# -----------------------------------------------------------------------------

def derive_obs_sources(uvsplit, freq):
    """Return the objects that were observed in an observation, including
    the primary calibrator (almost certainly 1934-638), the secondary,
    and the target sources.  
    
    Arguments:
        uvsplit {mirstr} -- Executed mirstr with the uvsplit output
        freq {str} -- The frequency of the observing data. Used as hook
                      to get out a source from
    """
    primary_srcs = ['1934-638']
    secondary_srcs = ['2245-328', '2312-319']
    target_srcs = ['a','b','c','d','e','f']

    primary = None
    secondary = None
    targets = []
    for l in uvsplit.split():
        if freq in l:
            src = l.split('.')[0]
            # 1934-628 should always be there
            if src in primary_srcs:
                primary = f"{src}.{freq}"
            elif src in secondary_srcs:
                secondary = f"{src}.{freq}"
            elif src in target_srcs:
                targets.append(f"{src}.{freq}")
            else:
                # Assume it is a mosaic source target
                targets.append(f"{src}.{freq}")

    if primary is None:
        logger.log(logging.ERROR, 'Primary is empty. Exiting.')
        sys.exit(0)
    
    if secondary is None:
        logger.log(logging.ERROR, 'Secondary is empty. Exiting.')
        sys.exit(0)

    if len(targets) == 0:
        logger.log(logging.ERROR, 'No target mosaic found. Exiting.')
        sys.exit(0)

    return primary, secondary, targets
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Multiband move operation
# -----------------------------------------------------------------------------

def mv_uv(freq:str):
    """Helper function to move uv files into directories consistently among days
    
    Arguments:
        freq {str} -- The frequency of the pipeline
    """
    if not os.path.exists('Plots'):
        # Potential race conditions
        try:
            os.makedirs('Plots')
        except:
            pass
        
    for f in glob(f'*{freq}.png') + glob(f'*{freq}_log.txt'):
        su.move(f, 'Plots')


    if not os.path.exists(f'f{freq}'):
        # Potential race conditions
        try:
            os.makedirs(f'f{freq}')
        except:
            pass
        
    for f in glob(f'*.{freq}'):
        su.move(f, f'f{freq}')


    if not os.path.exists('uv'):
        # Potential race conditions
        try:
            os.makedirs('uv')
        except:
            pass

    if freq == 5500:
        su.move('data5.uv', 'uv')
    elif freq == '9500':
        su.move('data9.uv', 'uv')

# -----------------------------------------------------------------------------

if __name__ == '__main__':

    uvsplit_test = """uvsplit vis=data9.uv options=mosaic

uvsplit: Revision 1.18, 2016/05/09 03:06:18 UTC

Creating 1934-638.9500
Creating 2245-328.9500
Creating d.9500"""

    print(derive_obs_sources(uvsplit_test, '9500'))
    print(derive_obs_sources(uvsplit_test, '5500'))

