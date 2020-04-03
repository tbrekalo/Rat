''' Set of utility functions used across the module '''

import os

def __check_paths( paths):
    ''' Checks if supplied path arguments are valid.

        Raises:
            FileNotFoundError
    '''

    for path in paths:
        if not os.path.exists(paths):
            raise FileNotFoundError(path)