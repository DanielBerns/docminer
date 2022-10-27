"""Example
"""

from exifread.tags import DEFAULT_STOP_TAG, FIELD_TYPES
from exifread import process_file, exif_log, __version__
from StringIO import StringIO

def example(img_file):

    detailed = True
    stop_tag = DEFAULT_STOP_TAG
    debug = False
    strict = False
    color = False
    data = None
    with open(img_file, 'rb') as source:
        content = StringIO(source.read())
        data = process_file(content, stop_tag=stop_tag, details=detailed, strict=strict, debug=debug)

    tag_keys = list(data.keys())
    tag_keys.sort()

    for i in tag_keys:
        try:
            print '"{0:s}" {1:s}: {2:s}'.format(i, FIELD_TYPES[data[i].field_type][2], data[i].printable)
        except:
            print "{0:s} : {1:s}".format(i, str(data[i]))
    
    print data["EXIF DateTimeDigitized"]

if __name__ == '__main__':
    example('/home/dberns/Documents/Code/docminer/2014-07-15_14-15-20.jpg')
