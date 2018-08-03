"""Helper script to create a new day of ATCA observing data given a 
set of rpfits files. It will attempt to create the appropriate 
directory structure, move files into place and copy a set of 
reduction scripts specific to that day. Logic is also implemented to
rename the junk files often create when a user sets up the telescope
"""

import os
import sys
import shutil as su

def add_reference_scripts(dest: str):
    """Add required reference scripts to the `dest` path
    
    Arguments:
        dest {str} -- Path to a day of data
    """
    pass


def process_files(files: list):
    """Create a new day of ATCA data given a set of files
    
    Arguments:
        files {list} -- RPFITS files to manage
    """
    sorted(files)
    print(files)
    
    # Get folder name
    date = files[0].split('_')[0]
    path = f'./{date}/raw'

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print(f'{date} folder exists at {path}. Exiting...')
        sys.exit(0)
    
    for f in files:
        dest = f"{path}/{f}"

        # User added new junk name
        if f.count('_') > 1:
            f = '_'.join(f.split('_')[:2])
            print('\t',f)

        # Move into place
        print(f"Moving {f} to {dest}")
        su.move(f, dest)



if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(f'USAGE: {sys.argv[0]} rpfits [rpfits ...]')
        sys.exit()

    elif sys.argv[1] in ['-h', '--help']:
        print(f'Call the {sys.argv[0]} script and pass in the rpfits files'\
            f' that would form a day. The date of the folder to create is'\
            f' is derived from the date of the first rpfits after being sorted.'\
            f' If you specify some suffix after an underscore (_) the script'\
            f' will move the correct rpfits file to that file name. This is useful'
            f' to nicely set aside ATCA data with set up data. \n\nNo options are required '\
            f' or implemented other then this help message.')
        sys.exit()

    else:
        files = sys.argv[1:]
        process_files(files)