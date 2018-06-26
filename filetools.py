from PIL import Image
from glob import glob
from zipfile import ZipFile
from os import path


def find_images(dir='./', callback: callable = None, recursive=True):
    image_extensions = ['jpg', 'png', 'jpeg']
    images = []
    for ext in image_extensions:
        matches = glob(f'{dir}/**/*.{ext}', recursive=recursive)
        if callback:
            matches = [i for i in matches if callback(i)]
        images += matches
    return images


def find_large_images(dir='./', max_megapixels=20, recursive=True):
    def image_is_large(file):
        with Image.open(file) as image:
            w, h = image.size
            megapixels = w * h / 1e6
            return megapixels >= max_megapixels

    return find_images(dir, callback=image_is_large, recursive=recursive)


def modify_filename(file, prefix='', suffix=''):
    dir = path.dirname(file)
    root, ext = path.splitext(path.basename(file))
    base = ''.join([prefix, root, suffix, ext])
    return path.join(dir, base)


def zip_files(files, zip_path, flat=False):
    with ZipFile(zip_path, 'w') as zf:
        for file in files:
            if flat:
                zf.write(file, arcname=path.basename(file))
            else:
                zf.write(file)
