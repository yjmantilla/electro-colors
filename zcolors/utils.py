import os

ALLOWED_EXTENSIONS = {'.png','.TIF' '.jpg', '.jpeg', '.gif','.bmp'}

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
                if any([x in name for x in ALLOWED_EXTENSIONS]):
                    filepaths.append(os.path.join(root, name))
            else:
                filepaths.append(os.path.join(root, name))
    return filepaths