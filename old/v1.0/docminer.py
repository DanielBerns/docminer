from os import walk
from os import makedirs
from os.path import join
from os.path import splitext
from os.path import getsize
from hashlib import md5
import sqlite3 as lite
from exifread.tags import DEFAULT_STOP_TAG
from exifread import process_file
from StringIO import StringIO

# os.walk(top, topdown=True, onerror=None, followlinks=False)
#    Generate the file names in a directory tree by walking the tree 
#    either top-down or bottom-up. For each directory in the tree rooted
#    at directory top (including top itself), 
#    it yields a 3-tuple (dirpath, dirnames, filenames).
#         dirpath is a string, the path to the directory. 
#         dirnames is a list of the names of the subdirectories in dirpath 
#         (excluding '.' and '..'). filenames is a list of the names of the 
#         non-directory files in dirpath. 
#    Note that the names in the lists contain no path components. 
#    To get a full path (which begins with top) to a file or directory in 
#    dirpath, do os.path.join(dirpath, name).

# Example
# http://www.pythoncentral.io/how-to-traverse-a-directory-tree-in-python-guide-to-os-walk/
# http://stackoverflow.com/questions/1698596/how-can-i-traverse-a-file-system-with-a-generator
#     import os
#     for root, dirs, files in os.walk(path):
#         for name in files:
#             print os.path.join(root, name)

# http://www.pythoncentral.io/introduction-to-sqlite-in-python/ 

class FileSystemWalker(object):
    def __init__(self, root):
        self._root = root
        
    def execute(self):
        for dirpath, dirnames, filenames in walk(self._root):
            for this_filename in filenames:
                fullpath = join(dirpath, this_filename)
                yield fullpath.decode('utf-8')


class FileSystemInfo(object):
    def __init__(self, walker):
        self._walker = walker
        
    def execute(self):
        for fullpath in self._walker.execute():
            filesize = getsize(fullpath)
            yield fullpath, filesize


class HashedContentProcessor(object):
    def __init__(self, walker):
        self._walker = walker
    
    def execute(self):
        for fullpath in self._walker.execute():
            with open(fullpath, 'r') as source:
                processor = md5()
                content = source.read()
                processor.update(content)
                hashed_content = processor.hexdigest()
                yield fullpath, hashed_content, content
  

MAX_NUMBER_OF_ENTRIES = 256

class FileStore(object):
    def __init__(self, root, maxlevels):
        self._root = root
        self._maxlevels = maxlevels - 1
        self._levels = None

    def get_path(self):
        levels = ['{0:03d}'.format(l) for l in self._levels[:-1]]
        return join(self._root, reduce(join, levels))

    def get_name(self):
        return '{0:03d}'.format(self._levels[-1])

    def start(self):
        self._levels = [0]*(self._maxlevels + 1)
        makedirs(self.get_path())
    
    def append(self, full_file_identifier, key, content, file_extension):
        target_identifier = join(self.get_path(), self.get_name()) + file_extension
        with open(target_identifier, 'wb') as target:
            target.write(content)
        cursor = self._maxlevels
        number = self._levels[cursor] + 1
        while MAX_NUMBER_OF_ENTRIES == number:
            self._levels[cursor] = 0
            cursor -= 1
            if cursor < 0:
                raise ValueError('FileStore.append: too many files')
            number = self._levels[cursor] + 1
        self._levels[cursor] = number
        if cursor < self._maxlevels:
            makedirs(self.get_path())            
            
    def stop(self):
        pass


class DocIndex(object):
    def __init__(self):
        self._counter = dict()
        self._docs = dict()
        self._instances = dict()

    def start(self):
        pass
    
    def append(self, full_file_identifier, key, content):
        self._instances[full_file_identifier] = key    
        try:
            value = self._counter[key]
            value += 1
            self._counter[key] = value
            return False
        except KeyError:
            value = 1
            self._counter[key] = value 
            self._docs[key] = full_file_identifier
            return True

    def stop(self):
        pass
    
    def get_docs(self):
        docs = list()
        number = 1
        for hexdigest, full_file_identifier in self._docs.iteritems():
            count = self._counter[hexdigest]
            docs.append((number, count, hexdigest, full_file_identifier))
            number += 1
        return docs
    
    def get_instances(self):
        instances = list()
        for full_file_identifier, hexdigest in self._instances.iteritems():
            instances.append((full_file_identifier, hexdigest))
        return instances


class ImageMetadata(object):
    def __init__(self):
        self._details = True
        self._stop_tag = DEFAULT_STOP_TAG
        self._debug = False
        self._strict = False
        self._color = False
        self._timestamps = dict()
    
    def start(self):
        pass
    
    def append(self, full_file_identifier, key, content, file_extension):
        if file_extension == '.jpg':
            try:
                source = StringIO(content)
                data = process_file(source, stop_tag=self._stop_tag, details=self._details, strict=self._strict, debug=self._debug)
                timestamp = repr(data["EXIF DateTimeDigitized"])[15:-6]
                self._timestamps[key] = timestamp
                return True
            except:
                return False
        else:
            return False

    def stop(self):
        pass

    def get_metadata(self):
        return [(value, key) for key, value in self._timestamps.iteritems()]

import pdb

class DocminerDatabase(object):
    def __init__(self, database_path, database_name='DocMiner-info.db'):
        self._database_full_identifier = join(database_path, database_name)

    def create(self):
        db = lite.connect(self._database_full_identifier)
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS Docs")
        cursor.execute("CREATE TABLE Docs(Number INT, Count INT, HexDigest TEXT, FirstInstance TEXT)")
        db.commit()
        cursor.execute("DROP TABLE IF EXISTS Instances")
        cursor.execute("CREATE TABLE Instances(Instance TEXT, HexDigest TEXT)")
        db.commit()
        cursor.execute("DROP TABLE IF EXISTS Metadata")
        cursor.execute("CREATE TABLE Metadata(Timestamp TEXT, HexDigest TEXT)")
        db.commit()
        db.close()

    def insert(self, docs, instances, metadata):
        db = lite.connect(self._database_full_identifier)
        cursor = db.cursor()
        cursor.executemany('INSERT INTO Docs VALUES(?, ?, ?, ?)', docs)
        db.commit()
        cursor.executemany('INSERT INTO Instances VALUES(?, ?)', instances)
        db.commit()
        pdb.set_trace()
        cursor.executemany('INSERT INTO Metadata VALUES(?, ?)', metadata)
        db.commit()
        db.close()


class DocMiner(object):
    def __init__(self, index, store, info, database): 
        self._index = index
        self._store = store
        self._info = info
        self._database = database

    def start(self):
        self._index.start()
        self._store.start()
        self._info.start()

    def append(self, full_file_identifier, key, content):
        if self._index.append(full_file_identifier, key, content):
            file_name, file_extension = splitext(full_file_identifier)
            file_extension = file_extension.lower()
            self._store.append(full_file_identifier, key, content, file_extension)
            self._info.append(full_file_identifier, key, content, file_extension)

    def stop(self):
        self._index.stop()
        self._store.stop()
        self._info.stop()
        self._database.create()
        self._database.insert(self._index.get_docs(), self._index.get_instances(), self._info.get_metadata())
