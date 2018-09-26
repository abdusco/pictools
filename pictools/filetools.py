from PIL import Image
from glob import glob
from zipfile import ZipFile
from os import path, scandir, rename
import re


def find_dirs_by_regex(parent: str, pattern: str):
    reg = re.compile(pattern=pattern, flags=re.IGNORECASE)
    dirs = []
    with scandir(parent) as it:
        for entry in it:
            if entry.is_file():
                continue
            base = path.basename(entry.path)
            if not reg.search(base):
                continue
            dirs.append(entry.path)
    return dirs


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


def numerate_images_in_dir(dir: str):
    images = sorted(find_images(dir))
    dir_name = path.basename(dir)
    for i, image in enumerate(images):
        dir = path.dirname(image)
        root, ext = path.splitext(path.basename(image))
        base = ''.join([dir_name, f'__{i + 1:03d}', ext])
        target_name = path.join(dir, base)
        rename(image, target_name)


def zip_files(files, zip_path, flat=False):
    with ZipFile(zip_path, 'w') as zf:
        for file in files:
            if flat:
                zf.write(file, arcname=path.basename(file))
            else:
                zf.write(file)


def readable_size(size, decimal_places=2):
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"
