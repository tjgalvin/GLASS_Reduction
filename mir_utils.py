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
# Multiband move operation
# -----------------------------------------------------------------------------

def mv_uv(mode:str):
    """Helper function to move uv files into directories consistently among days
    
    Arguments:
        mode {str} -- The mode of calibration (notsys/normal)
    """
    if mode == 'notsys':
        suffix = '_notsys'
    else:
        suffix = ''
    
    # Move the rpfit -> miriad files
    if not os.path.exists(f'uv{suffix}'):
        os.mkdir(f'uv{suffix}')
    su.move(f'data1.uv', f'uv{suffix}')
    su.move(f'data2.uv', f'uv{suffix}')
    
    # Move the ifsel1 source files
    if not os.path.exists(f'f7700{suffix}'):
        os.mkdir(f'f7700{suffix}')
    for uv in glob('*.7700'):
        su.move(uv, f'f7700{suffix}')

    # Move the ifsel2 source files
    if not os.path.exists(f'f9500{suffix}'):
        os.mkdir(f'f9500{suffix}')
    for uv in glob('*.9500'):
        su.move(uv, f'f9500{suffix}')

        
        # Move the ifsel2 source files
    if not os.path.exists(f'Plots{suffix}'):
        os.mkdir(f'Plots{suffix}')
    for uv in glob('*.png'):
        su.move(uv, f'Plots{suffix}')
    for txt in glob('*.txt'):
        su.move(txt, f'Plots{suffix}')

# -----------------------------------------------------------------------------

