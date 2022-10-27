from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import binascii
import shutil
from subprocess import run
from subprocess import CalledProcessError
from argparse import ArgumentParser

from sources import LabelledFullPathSource
from hexastore import HexaStore
from parameters import Parameters
from picklestore import read_pk
from picklestore import write_pk

class Collector:
    def __init__(self, collection_url):
        collection_path = Path(collection_url).expanduser().absolute()
        instances_path = Path(collection_path, 'instances.pk')
        if collection_path.exists():
            instances = read_pk(instances_path)
        else:
            collection_path.mkdir(mode=0o700, parents=True)
            instances = defaultdict(list)
        self._instances = instances
        self._instances_path = instances_path

    def handle_content(self):
        pass
    
    def append(self, file_path, label):
        if file_path.is_symlink():
            file_path = file_path.resolve()
        with open(file_path, 'rb') as target:
            content = target.read()
            processor = sha256()
            processor.update(content)
            key = processor.digest()
            self._instances[key].append((file_path, label))

    def read(self, source):
        for file_path, label in source.read():
            self.append(file_path, label)
    
    def instances(self):
        number = 0
        for key, labels_list in self._instances.items():
            yield number, key, labels_list
            number += 1

    @property
    def instances_path(self):
        return self._instances_path

    def content(self, file_path):
        name = file_path.name 
        parts = name.split('.')
        return parts[-1]
        
    def write(self, store):
        total_instances = len(self._instances.keys())
        labels_per_key = defaultdict(list)
        for number, key, labels_list in self.instances():
            print('{0:d} / {1:d}'.format(number, total_instances))
            file_path, label = labels_list[0]
            new_sample = store.new_sample()
            new_sample.mkdir(mode=0o700, parents=True)
            self.handle_content(file_path, new_sample)
            metadata_path = Path(new_sample, 'metadata.md')
            with open(metadata_path, 'w') as target:
                target.write('# metadata\n\n')
                target.write('## file_path\n\n')
                target.write('{0:s}\n\n'.format(str(file_path)))
                target.write('## key\n\n')
                ascii_key = binascii.hexlify(key).decode('utf8')
                target.write('{0:s}\n\n'.format(ascii_key))
                target.write('## number\n\n')
                target.write('{0:d}\n\n'.format(number))
                target.write('## labels\n')
                for item in labels_list:
                    target.write('* {0:s}\n'.format(item[1]))
                target.write('\n\n')
        write_pk(self.instances, self.instances_path)


class CopyContentCollector(Collector):
    def __init__(self, collection_url):
        super().__init__(collection_url)
    
    def handle_content(self, file_path, new_sample):
        print('Processing {0:s} - {1:s}'.format(str(file_path), str(new_sample)))
        name = file_path.name
        parts = name.split('.')
        extension = parts[-1]
        target = Path(new_sample, 'content.' + extension)
        text = Path(new_sample, 'content.' + 'html')
        shutil.copy(file_path, target)
        try:
            run(['pdftotext', '-htmlmeta', str(target), str(text)], check=True)
        except CalledProcessError:
            print('Error found extracting text from {0:s}'.format(str(target)))
        return target


class LinkContentCollector(Collector):
    def __init__(self, collection_url):
        super().__init__(collection_url)
    
    def handle_content(self, file_path, new_sample):
        print('Processing {0:s} - {1:s}'.format(str(file_path), str(new_sample)))
        name = file_path.name
        parts = name.split('.')
        extension = parts[-1]
        target = Path(new_sample, 'content.' + extension)
        text = Path(new_sample, 'content.' + 'html')
        target.symlink_to(file_path)
        try:
            run(['pdftotext', '-htmlmeta', str(target), str(text)], check=True)
        except CalledProcessError:
            print('Error found extracting text from {0:s}'.format(str(target)))
        return target

def get_cli_arguments():
    ap = ArgumentParser()
    ap.add_argument("-s", "--source_url", required=True, help="path to the source directory")
    ap.add_argument("-t", "--target_url", required=True, help="path to the target directory")
    return vars(ap.parse_args())

if __name__ == '__main__':
    cli_arguments = get_cli_arguments()
    code_arguments = None
    parameters = Parameters('docminer', cli_arguments, code_arguments)
    source = FilePathSource(parameters.source_url, ('pdf'))
    store_url = parameters.target_url + '/store'
    collection_url = parameters.target_url + '/collector'    
    store = HexaStore(store_url)
    collector = CopyContentCollector(collection_url)
    collector.read(source)
    collector.write(store)
    store.close()
