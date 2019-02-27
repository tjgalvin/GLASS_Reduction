"""Script to reduce 5.5GHz data from GLASS
"""
import mir_utils as mu
from pymir import mirstr as m
from multiprocessing import Pool
from glob import glob
import logging
import os
import shutil as su

logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("calibration_if1_5500.log", mode='w'),
        logging.StreamHandler()
    ])

logger = logging.getLogger()

def run(a):
    a.run()
    # logger.log(logging.INFO, a)

NFBIN = 4
FREQ = 5500

# Load in files assuming the setup file/s have been renamed or deleted
files = glob('raw/*C3132')

# Example loading in files assuming first is setup
# files = glob('raw/*C3132').pop(0)

# Glob order is not the same as sort order
# Can lead to problems with 0 and 9s. 
files = sorted(files)

# Load in data. Remember to set ifsel appropriately
atlod = m(f"atlod in={','.join(files)} out=data5.uv ifsel=1 options=birdie,rfiflag,noauto,xycorr").run()
logger.log(logging.INFO, atlod)

# Flag out known bad channels
mu.uvflag(atlod.out, mu.flags_5)

uvsplit = m(f"uvsplit vis={atlod.out} options=mosaic").run()
logger.log(logging.INFO, uvsplit)

# Deduce the objects in the observing run
srcs = mu.derive_obs_sources(uvsplit, FREQ)
primary, secondary, mosaic_targets = srcs

mu.calibrator_pgflag(primary)

mfcal = m(f"mfcal vis={primary} refant=4 interval=0.1").run()
logger.log(logging.INFO, mfcal)

gpcal = m(f"gpcal vis={primary} refant=4 interval=0.1 nfbin={NFBIN} options=xyvary").run()
logger.log(logging.INFO, gpcal)

mu.calibrator_pgflag(primary)

mfcal = m(f"mfcal vis={primary} refant=4 interval=0.1").run()
logger.log(logging.INFO, mfcal)

gpcal = m(f"gpcal vis={primary} refant=4 interval=0.1 nfbin={NFBIN} options=xyvary").run()
logger.log(logging.INFO, gpcal)

gpcopy = m(f"gpcopy vis={primary} out={secondary}").run()
logger.log(logging.INFO, gpcopy)

mu.calibrator_pgflag(secondary)

gpcal = m(f"gpcal vis={secondary} refant=4 interval=0.1 nfbin={NFBIN} options=xyvary,qusolve").run()
logger.log(logging.INFO, gpcal)

mu.calibrator_pgflag(secondary)

gpcal = m(f"gpcal vis={secondary} refant=4 interval=0.1 nfbin={NFBIN} options=xyvary,qusolve").run()
logger.log(logging.INFO, gpcal)

gpboot = m(f"gpboot vis={secondary} cal={primary}").run()
logger.log(logging.INFO, gpboot)

mfboot = m(f"mfboot vis={primary},{secondary} select=source(1934-638) device=mfboot_{FREQ}.png/png").run()
logger.log(logging.INFO, mfboot)

mu.calibration_plots(primary, secondary, FREQ)

for mosaic in mosaic_targets:

    gpcopy = m(f"gpcopy vis={secondary} out={mosaic}").run()
    logger.log(logging.INFO, gpcopy)

    srcs = mu.mosaic_uvsplit(mosaic)

    for src in srcs:
        mu.mosaic_src_calibration(src)

        mu.mosaic_src_pgflag(src)

    mu.mv_srcs(srcs, FREQ)
    mu.mv_mosaic(mosaic)


mu.mv_calibrators(primary, secondary)
mu.mv_calibrators(atlod.out, FREQ)
mu.mv_plots(FREQ)
