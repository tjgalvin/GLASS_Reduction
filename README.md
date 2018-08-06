# GLASS_Reduction

This repository is a test of a somewhat automated pipeline to help *calibrate* the ATCA GLASS (C3132) project. Throughout each observing semester GLASS is typically awarded 400 hours across ~35 days. Automating this process as much as possible is critical. 

Results of the pipeline should be committed and uploaded to this repository so that they can be easily inspected by others. 

The majority of modules should be in the standard python library. There are two main requirements for this pipeline. 
- Miriad
- `pymir` (https://github.com/tjgalvin/pymir) 

`pymir` is a simple helper class to process miriad commands. Although there are other libraries (`mirpy` for instance, or the simple `os.call`) I don't like them for one reason or anything.

## new_day.py

Script to move ATCA RPFITS files into their own directory. Ideally, this should be executed in a directory from within the `Data` directory. For instance `Data/to_proc`. 

It has logic built in to allow filenames to be provided with an additional suffix added by the user, highlighting that certain files are junk files. This is useful to allow a single glob expression to be used when performing `atlod`. 

The script will also copy `reduce_5.py` and `reduce_9.py` into the directory, and symlink to `mir_utils.py`. The name of the new directory is creates in the `Data` folder is the date of the first RPFITS file. 

A typical invocation of `new_day.py` is:

`python3 ../../new_day.py 2016-11-06_0403.C3132_setup 2016-11-07_0430.C3132 2016-11-07_0717.C3132 2016-11-07_1*`

Note the `_setup` added to the first RPFITS file, and the glob at the end. The relative path also indicates the script being executed in a folder within `Data`.

*At the moment relative paths are hardcoded. Its important to ensure the script is executed within a directory in `Data`. A proper `argparse` CLI will be added soon.*

## mir_utils.py

A script containing common logic that should be shared across all days. It implements:
- deducing calibrator/target names
- calibrator flagging
- mosaic field flagging
- moving items into consistent directories

Each individual day of data will have a symlink to this file. 

## reduce_5.py and reduce_9.py

Processing scripts to handle each of the ATCA CABB IFs. Although the basic calibration procedure is the same for CABB across both bands, it might be best to keep separate scripts. This would allow any day and IF specific actions to be maintained separately. For instance, if extra flagging has to be performed due to particularly bad RFI or a CABB block going offline. 
