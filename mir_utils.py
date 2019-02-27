"""Utilities to help with the execution of miriad tasks and C3171 project data. 
"""
from glob import glob
import subprocess as sp
import pymir as pymir
from pymir import mirstr as m
from multiprocessing import Pool
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

# flags_5 = {'chan_start':[None],
#            'chan_end'  :[None]}

ref_5 = 4476
flags_5 = {'chan_start':[5622-ref_5, 5930-ref_5, 6440-ref_5],
           'chan_end'  :[5628-ref_5, 5960-ref_5, 6480-ref_5]}

ref_9 = 8476
flags_9 = {'chan_start':[850],
           'chan_end'  :[915]}


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
    if len(flag_def['chan_start']) != len(flag_def['chan_end']):
        raise ValueError('Channels start and end should have the same length')
        
    for start, end in zip(flag_def['chan_start'], flag_def['chan_end']):
        line = f"chan,{end-start},{start},1"
        proc = mirstr(f"uvflag vis={vis} line={line} flagval=flag").run()
        logger.log(logging.INFO, proc)


def calibrator_pgflag(src):
    """A series of pgflag steps common to most (if not all) of
    the primary and secondary miriad uv files.

    This is following the flagging outlined in Do_Flag.csh` on the
    ATCAGAMA wiki
    
    Arguments:
        src {str} -- The filename of the data to flag
    """
    primary = True if '1934-638' in src else False

    if primary:
        pgflag = m(f"pgflag vis={src} stokes=v flagpar=15,3,3,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)
        
        pgflag = m(f"pgflag vis={src} stokes=q flagpar=15,3,3,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)
        
        pgflag = m(f"pgflag vis={src} stokes=u flagpar=15,3,3,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)
        
        pgflag = m(f"pgflag vis={src} stokes=i flagpar=15,3,3,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)
    
    else:
        pgflag = m(f"pgflag vis={src} stokes=i,q,u,v flagpar=10,1,1,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)
        
        pgflag = m(f"pgflag vis={src} stokes=i,u flagpar=10,1,1,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)
        
        pgflag = m(f"pgflag vis={src} stokes=i,q flagpar=10,1,1,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)
        
        pgflag = m(f"pgflag vis={src} stokes=i flagpar=10,1,1,3,5,3 command='<' options=nodisp").run()
        logger.log(logging.INFO, pgflag)  


def mosaic_pgflag(src):
    """Thw flagging procedure applied to the source data. THis follows Minh's script
    called Do_Flag.csh on the ATCAGAMA wiki. For ease it is applied before uvsplit. 
    Time convolution is turned off for the moment. 
    
    Arguments:
        src {[type]} -- [description]
    """
    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q,u,v flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q,u,v flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,u flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,u flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 

    pgflag = m(f"pgflag vis={src} command='<' stokes=i flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 
    

def mosaic_src_pgflag(src):
    """Thw flagging procedure applied to the source data. THis follows Minh's script
    called Do_Flag.csh on the ATCAGAMA wiki. For ease it is applied before uvsplit. 
    Time convolution is turned off for the moment. 
    
    Arguments:
        src {[type]} -- [description]
    """
    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q,u,v flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q,u,v flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,q flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,u flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i,u flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 

    pgflag = m(f"pgflag vis={src} command='<' stokes=i flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag)

    pgflag = m(f"pgflag vis={src} command='<' stokes=i flagpar=10,1,0,3,5,3  "\
               f"options=nodisp").run()
    logger.log(logging.INFO, pgflag) 


# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Common calibration utilities
# -----------------------------------------------------------------------------
def mosaic_src_calibration(src: str):
    """Apply any common calibration steps for each source file
    
    Arguments:
        src {str} -- uv source file of item to process
    """
    gpaver = m(f"gpaver vis={src} interval=5 options=scalar").run()
    logger.log(logging.INFO, gpaver)

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Common plotting utilities
# -----------------------------------------------------------------------------
def run(a):
    a.run()

def calibration_plots(primary: str, secondary: str, freq: str):
    """Common function to create calibration plots of the primary and
    secondary visibility files
    
    Arguments:
        primary {str} -- Filename of primary calibrator
        secondary {str} -- Filename of the secondary calibrator
        freq {str} -- Frequency of the IF
    """
    plt = [m(f'uvplt vis={primary} axis=time,amp options=nob,nof stokes=i device=primary_timeamp_{freq}.png/PNG'),
            m(f'uvplt vis={primary} axis=re,im options=nob,nof,eq stokes=i,q,u,v device=primary_reim_{freq}.png/PNG'),
            m(f'uvplt vis={primary} axis=uc,vc options=nob,nof stokes=i  device=primary_ucvc_{freq}.png/PNG'),
            m(f'uvplt vis={primary} axis=FREQ,amp options=nob,nof stokes=i  device=primary_freqamp_{freq}.png/PNG'),
            m(f'uvplt vis={secondary} axis=time,amp options=nob,nof stokes=i device=secondary_timeamp_{freq}.png/PNG'),
            m(f'uvplt vis={secondary} axis=re,im options=nob,nof,eq stokes=i,q,u,v device=secondary_reim_{freq}.png/PNG'),
            m(f'uvplt vis={secondary} axis=uc,vc options=nob,nof stokes=i  device=secondary_ucvc_{freq}.png/PNG'),
            m(f'uvplt vis={secondary} axis=FREQ,amp options=nob,nof stokes=i device=secondary_freqamp_{freq}.png/PNG'),
            m(f'uvfmeas vis={secondary} stokes=i log=secondary_uvfmeas_{freq}_log.txt device=secondary_uvfmeas_{freq}.png/PNG')]
    pool = Pool(7)
    result = pool.map(run, plt)
    pool.close()
    pool.join()

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Source book keeping operations
# -----------------------------------------------------------------------------

def mosaic_uvsplit(mosaic: str):
    """uvsplit a mosaic source file up based on source names. Will return
    a list of new source files to operate upon. 
    
    Arguments:
        mosaic {str} -- Name of the mosaic file to split
    """
    uvsplit = m(f"uvsplit vis={mosaic}").run()
    logger.log(logging.INFO, uvsplit)

    srcs = []
    for line in str(uvsplit).splitlines():
        if 'Creating' not in line:
            continue
        srcs.append(line.split()[1])

    return srcs

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
    secondary_srcs = ['2245-328', '2312-319', '2255-282']
    target_srcs = ['a','b','c','d','e','f']
    ignore_srcs = ['2333-528','0823-500','0537-441','1921-293']

    freq = f"{freq}"

    primary = None
    secondary = None
    targets = []

    for l in str(uvsplit).split():
        if freq in l:
            src = l.split('.')[0]
            # 1934-628 should always be there
            if src in primary_srcs:
                primary = f"{src}.{freq}"
            elif src in secondary_srcs:
                secondary = f"{src}.{freq}"
            elif src in target_srcs:
                targets.append(f"{src}.{freq}")
            elif src in ignore_srcs:
                pass
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

def make_dir(directory: str):
    """Make up a directory
    
    Arguments:
        dir {str} -- make up a directory
    """
    if not os.path.exists(directory):
        # Potential race conditions between checking and creating
        try:
            os.makedirs(directory)
        except:
            pass


def mv_srcs(srcs: list, freq: str):
    """Move sources into a consistent directory structure

    Arguments:
        srcs {list} -- List of source files to move into place
        freq {str} -- Frequency of data
    """
    if not isinstance(srcs, list):
        srcs = [srcs,]

    freq = str(freq)
    folder = f"f{freq}_sources"
    
    make_dir(folder)
    for src in srcs:
        su.move(src, folder)


def mv_mosaic(mosaic: str):
    """Move a mosaic file into a folder
    
    Arguments:
        mosaic {str} -- Mosaic file to move
        freq {str} -- Frequency of the file
    """
    freq = str(freq)
    folder = f"uv_mosaic"

    make_dir(folder)
    su.move(mosaic, folder)


def mv_data(data: str):
    """Move the data uv file from atlod into place
    
    Arguments:
        data {str} -- The data file from atlod
    """
    folder = f"data_uv"

    make_dir(folder)
    su.move(data, folder)


def mv_calibrators(primary: str, secondary: str):
    """Move the calibrators into place
    
    Arguments:
        primary {str} -- Name of the primary calibrator
        secpmdary {str} -- Name of the secondary calibrator
    """
    folder = "uv_calibrators"

    make_dir(folder)
    su.move(primary, folder)
    su.move(secondary, folder)


def mv_plots(freq: str):
    """Move the plots from the scripts into place
    
    Arguments:
        freq {str} -- Frequency of the plots to move
    """
    folder = 'Cal_Plots'
    make_dir(folder)

    for f in glob(f'*{freq}.png') + glob(f'*{freq}_log.txt'):
        su.move(f, 'Plots')


def mv_uv(freq:str, old=False):
    """Helper function to move uv files into directories consistently among days
    
    Arguments:
        freq {str} -- The frequency of the pipeline

    Keyword Arguments {bool} -- If old, retain the original folder scheme 
    """
    suffix = '' if old is True else '_minh'
    if not isinstance(freq, str):
        freq = str(freq)

    if not os.path.exists('Plots'):
        # Potential race conditions
        try:
            os.makedirs('Plots')
        except:
            pass
        
    for f in glob(f'*{freq}.png') + glob(f'*{freq}_log.txt'):
        su.move(f, 'Plots')


    if not os.path.exists(f'f{freq}{suffix}'):
        # Potential race conditions
        try:
            os.makedirs(f'f{freq}{suffix}')
        except:
            pass
        
    for f in glob(f'*.{freq}'):
        su.move(f, f'f{freq}{suffix}')


    if not os.path.exists(f'uv{suffix}'):
        # Potential race conditions
        try:
            os.makedirs(f'uv{suffix}')
        except:
            pass

    if freq == '5500':
        su.move('data5.uv', f'uv{suffix}')
    elif freq == '9500':
        su.move('data9.uv', f'uv{suffix}')

# -----------------------------------------------------------------------------

if __name__ == '__main__':

    uvsplit_test = """uvsplit vis=data9.uv options=mosaic

uvsplit: Revision 1.18, 2016/05/09 03:06:18 UTC

Creating 1934-638.9500
Creating 2245-328.9500
Creating d.9500"""

    print(derive_obs_sources(uvsplit_test, '9500'))
    print(derive_obs_sources(uvsplit_test, '5500'))

