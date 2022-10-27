import os
from pathlib import Path
import random


def list_full_paths(base_path, valid_extensions):
    # loop over the directory structure
    for (root, directories, filenames) in os.walk(base_path):
        # loop over the filenames in the current directory
        for filename in filenames:
            # determine the file extension of the current file
            extension = filename[filename.rfind(".")+1:].lower()

            # check to see if the file should be processed
            if extension.endswith(valid_extensions):
                # construct the path to the image and yield it
                full_path = Path(root, filename)
                yield full_path, root


class FilePathSource:
    def __init__(self, base, valid_extensions):
        base_path = Path(base).expanduser().absolute()        
        self._base_path = base_path
        self._valid_extensions = valid_extensions
    
    @property
    def base_path(self):
        return self._base_path
    
    def read(self):
        length = len(str(self.base_path))
        for full_path, root in list_full_paths(self.base_path, valid_extensions=self._valid_extensions):
            label = root[length:]
            yield (full_path, label)

