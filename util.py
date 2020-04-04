''' Utility functions used across Meta-Rat '''

import os
import sys
import shutil


def check_path(file_path):
    ''' Checks whether file/dir exists.
        Returns path string representation.

        Raises:
            FileNotFoundError '''

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    return file_path


def clean_dir(dir_path):
    ''' Removes all files in a folder and unlinks sym-links

        Args:
            dir_path: path to target directory 

    '''

    def gen_file_path(filename): return os.path.join(dir_path, filename)

    for file_path in map(gen_file_path, os.listdir(dir_path)):
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('[ERROR] Failed to delete {}\n Message: {}'.foramt(
                file_path, e), file=sys.stderr)

    pass


def create_clean_dir(parent_path, name, parent_checked=False):
    ''' Creates a new directory in parent directory
        or remove all files directory already exists 
        
        Returns:
            dir_path: str path to clean directory
    '''

    if not parent_checked:
        check_path(parent_path)    
    
    dir_path = os.path.join(parent_path, name)
    
    if os.path.exists(dir_path):
        clean_dir(dir_path)
    else:
        os.mkdir(dir_path)

    return dir_path

