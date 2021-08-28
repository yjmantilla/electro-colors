import os

ALLOWED_EXTENSIONS = {'.png','.TIF' ,'.jpg', '.jpeg', '.gif','.bmp'}

def _get_files(root_path,ALLOWED_EXTENSIONS=None):
    """Recursively scan the directory for files, returning a list with the full-paths to each.
    
    Parameters
    ----------
    root_path : str
        The path we want to obtain the files from.
    Returns
    -------
    filepaths : list of str
        A list containing the path to each file in root_path.

    ALLOWED_EXTENSIONS: iterable
        Iterable with the allowed extensions. If None, all files will be accepted.
    """
    filepaths = []
    for root, dirs, files  in os.walk(root_path, topdown=False):
        for name in files:
            if ALLOWED_EXTENSIONS is not None:
                if is_valid_file(name):
                    filepaths.append(os.path.join(root, name))
            else:
                filepaths.append(os.path.join(root, name))
    return filepaths

def is_valid_file(x):
    return any([y in x for y in ALLOWED_EXTENSIONS])

def splitall(path):
    """https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html"""
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts