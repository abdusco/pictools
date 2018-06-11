from os import makedirs, path, rename
from PIL import Image


def separate_by_orientation(images, out='./', verbose=False):
    dirs = {
        'portrait': {
            'created': False,
            'path': path.realpath(path.join(out, 'portrait'))
        },
        'wide': {
            'created': False,
            'path': path.realpath(path.join(out, 'wide'))
        }
    }

    for file in images:
        with Image.open(file) as image:
            w, h = image.size

        if w > h:
            target = dirs['portrait']
        else:
            target = dirs['wide']
        if not target['created']:
            makedirs(target['path'])
            target['created'] = True

        if verbose:
            print(f'Moving {file} to {target["path"]}')

        rename(file, path.join(target['path'], path.basename(file)))


def separate_by_first_segment(images, out='./', separator=' - ', verbose=False):
    for file in images:
        dir = path.dirname(file)
        base = path.basename(images)
        root, ext = path.splitext(base)
        segments = root.split(separator)
        if not len(segments) > 1:
            print(f'Skipping {base}, no segments')
            continue
        target = path.join(dir, out, segments[0], base)
        rename(file, target)
