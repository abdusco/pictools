from PIL import Image
from filetools import modify_filename
from os import path


def resize_image(file, save_path, max_length=0, width=0, height=0, quality=80):
    if not max_length and not width and not height:
        raise AssertionError('At least one dimension must be specified')

    with Image.open(file) as image:
        w, h = image.size

        is_portrait = h >= w
        is_larger_than_max = max_length and max(w, h) > max_length
        resize_by_width = width != 0 and height == 0 and not max_length
        resize_by_height = height != 0 and width == 0 and not max_length

        if is_larger_than_max:
            if is_portrait:
                height = max_length
                width = height / h * w
            else:
                width = max_length
                height = width / w * h
        elif resize_by_width:
            height = width * h / w
        elif resize_by_height:
            width = height * w / h

        if width or height:
            image = image.resize((int(width), int(height)), Image.LANCZOS)
        image.save(save_path, quality=quality, mode='JPEG')


def process_images(images, max_length=5000, quality=80, prefix='r__', suffix='', verbose=False, force=False):
    for f in images:
        base = path.basename(f)
        root, _ = path.splitext(base)
        save_path = modify_filename(f, prefix=prefix, suffix=suffix)

        is_processed_image = (bool(prefix) and root.startswith(prefix)) or (bool(suffix) and root.endswith(suffix))
        is_processed = path.exists(save_path)

        if is_processed_image:
            continue

        if is_processed and not force:
            print(f'Skipping: {base}')
            # make sure processed images are passed downstream
            yield save_path
            continue

        if verbose:
            print(f'Processing: {base}')

        resize_image(f, save_path, max_length=max_length, quality=quality)

        if verbose:
            newsize, oldsize, delta = get_sizes(new=save_path, old=f)
            percent = delta / oldsize * 100
            newsize, oldsize = newsize / 1e6, oldsize / 1e6
            print(f'\tDone: {oldsize:.2f}MB -> {newsize:.2f}MB ({percent:.1f}%)')

        yield save_path


def get_sizes(new, old):
    newsize = path.getsize(new)
    oldsize = path.getsize(old)
    delta = newsize - oldsize
    return newsize, oldsize, delta
