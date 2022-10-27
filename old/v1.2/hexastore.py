#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime


class HexaStoreError(Exception):
    def __init__(self, message):
        super().__init__(message)


def hexabyte(n):
    return ('{0:>02x}'.format(n)).upper()


class HexaStore:
    """
         base: path where the hexa storage lives
    """
    def __init__(self, base, prefix='data', metadata_filename='index.json'):
        """
        """
        base_path = Path(base).expanduser()
        prefix_path = Path(base_path, prefix)
        metadata_path = Path(base_path, metadata_filename)
        if not prefix_path.exists():
            prefix_path.mkdir(mode=0o700, parents=True)
            with open(metadata_path, 'w') as target:
                metadata = {'index': 0}
                as_json = json.dumps(metadata)
                target.write('{0:s}'.format(as_json))
            index = 0
        else:
            if metadata_path.exists():
                with open(metadata_path, 'r') as source:
                    for line in source:
                        try:
                            metadata = json.loads(line)
                            index = metadata['index']
                        except ValueError:
                            raise HexaStoreError('Wrong HexaStore metadata')
                        break
            else:
                raise HexaStoreError('No metadata found')                
        self._base = base_path
        self._prefix_path = prefix_path
        self._metadata = metadata_path
        self._index = index
        
    @property
    def index(self):
        return self._index

    def new_sample(self):
        hexa = ('{0:>06x}'.format(self._index)).upper()
        root = Path(self._prefix_path, hexa[0:2], hexa[2:4])
        if not root.exists():
            root.mkdir(mode=0o700, parents=True)
        sample = Path(root, hexa)
        self._index += 1
        return sample

    def close(self):
        with open(self._metadata, 'w') as target:
            target.write('{0:d}'.format(self._index))
        
    def samples(self, top=-1):
        if top == -1:
            top = self._index
        elif 0 <= top <= self._index:
            pass
        else:
            raise HexaStoreError("HexaStore.samples: top {0:d} out of range (0, {1:d})".format(top, self._index))
        for k in range(top):
            hexa = ('{0:>06x}'.format(k)).upper()
            sample = Path(self._base, 'data', hexa[0:2], hexa[2:4], hexa)
            yield sample
