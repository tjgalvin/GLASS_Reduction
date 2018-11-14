"""Script to batch run the uvfmeas task using the secondary visibility data

Need to add option to handle this. 
"""
import os
import sys
import glob
import pymir as mu
from multiprocessing import Pool
import subprocess as sp

def run(s):
    """Function to call uvfmeas
    
    Arguments:
        s {tuple} -- Element one is the calibration working directory to execute in
    """
    secondary_srcs = ['2245-328', '2312-319', '2255-282']
    secondary = None

    if not os.path.exists(f"{s}/f5500/"):
        return

    srcs = os.listdir(f"{s}/f5500/")
    for src in srcs:
        src = src.replace('.5500','')
        if src in secondary_srcs:
            secondary = src

    secondary_5 = f"{s}/f5500/{secondary}.5500"
    secondary_9 = f"{s}/f9500/{secondary}.9500"

    if os.path.exists(secondary_5) and os.path.exists(secondary_9):
        uvfmeas = f"uvfmeas vis={secondary_5},{secondary_9} stokes=i "\
                  f"device={s}/Plots/secondary_both.png/PNG "\
                  f"log={s}/Plots/secondary_both.txt"
        print(uvfmeas)

        uvfmeas = mu.mirstr(uvfmeas).run()
        print(uvfmeas)


# Should be OK for the moment. No data in 2020's yet
if len(sys.argv) > 1:
    # Assume user knows what they are doing
    days = sys.argv[1:]
else:
    days = glob.glob('Data/201*')

pool = Pool(10)
result = pool.map(run, days)
pool.close()
pool.join()