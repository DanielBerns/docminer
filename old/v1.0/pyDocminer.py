import docminer

ROOT = '/home/dberns/Documents/Classify/'
STORE = '/home/dberns/Documents/Datasets/docminer'
DATABASE = '/home/dberns/Documents/Databases/docminer'

walker = docminer.FileSystemWalker(ROOT)
iterator = docminer.HashedContentProcessor(walker)
index = docminer.DocIndex()
store = docminer.FileStore(STORE, 2)
metadata = docminer.ImageMetadata()
database = docminer.DocminerDatabase(DATABASE)

agent = docminer.DocMiner(index, store, metadata, database)
agent.start()
for full_file_identifier, hexdigest, content in iterator.execute():
    agent.append(full_file_identifier, hexdigest, content)
agent.stop()
