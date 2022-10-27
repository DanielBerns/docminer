import unittest
import docminer 

ROOT = '/home/dberns/Documents/Info/Themes/'

class TestDocMiner(unittest.TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    #def test_FileSystemInfo(self):
        #walker = docminer.FileSystemWalker(ROOT)
        #iterator = docminer.FileSystemInfo(walker)
        #counter = 0
        #totalsize = 0
        #for fullpath, filesize in iterator.execute():
            #counter += 1
            #totalsize = filesize
        #print 'files: ', counter, '- totalsize: ', totalsize

    def test_FileSystemFullPath(self):
        walker = docminer.FileSystemWalker(ROOT)
        iterator = docminer.HashedContentProcessor(walker)
        for fullpath, hexdigest, content in iterator.execute():
            print('{0:s} - {1:s}'.format(fullpath, hexdigest))


    def test_FileStore(self):
        store = docminer.FileStore('./Store', 3)
        store.start()
        for k in range(256*256):
            store.append('{0:010d}'.format(k), 'txt')
        store.stop()
        
if __name__ == '__main__':
    unittest.main() 
