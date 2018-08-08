from PIL import Image
from filetools import modify_filename, readable_size
from os import path
from operator import sub

# suppress compression bomb warnings
Image.MAX_IMAGE_PIXELS = 100 ** 6


def _calculate_dimensions(size: tuple, max_length, max_width, max_height):
    w, h = size
    is_portrait = h >= w
    by_max_length = max_length and max(w, h) > max_length
    by_max_width = max_width and not (max_height or max_length) and w > max_width
    by_max_height = max_height and not (max_width or max_length) and h > max_height

    if by_max_length:
        if is_portrait:
            h, w = max_length, max_length / h * w
        else:
            w, h = max_length, max_length / w * h
    elif by_max_width:
        h = max_width / w * h
    elif by_max_height:
        w = max_height / h * w

    return int(w), int(h)


def resize_image(file, save_path, max_length=0, max_width=0, max_height=0, quality=80):
    assert max_length or max_width or max_height, 'At least one dimension must be specified'

    with Image.open(file) as image:
        dimensions = image.size
        calculated = _calculate_dimensions(dimensions,
                                           max_length=max_length,
                                           max_width=max_width,
                                           max_height=max_height)
        if dimensions != calculated:
            image = image.resize(calculated, Image.LANCZOS)
        image.save(save_path, quality=quality, mode='JPEG')


def process_images(images, max_length=5000, quality=80, prefix='r__', suffix='', verbose=True, force=False):
    processed = []
    due = []
    for image_path in images:
        base = path.basename(image_path)
        root, _ = path.splitext(base)
        save_path = modify_filename(image_path, prefix=prefix, suffix=suffix)

        is_processed_image = (prefix and root.startswith(prefix)) or (suffix and root.endswith(suffix))
        was_processed = path.exists(save_path)

        if is_processed_image:
            continue

        if was_processed and not force:
            if verbose:
                print(f'ALREADY PROCESSED: {base}')
            # make sure processed images are passed downstream
            processed.append(save_path)
            continue
        due.append(image_path)

    total_due = len(due)
    for i, image_path in enumerate(due):
        save_path = modify_filename(image_path, prefix=prefix, suffix=suffix)
        base = path.basename(image_path)

        print(f'PROCESSING [{i + 1}/{total_due}]: {base} ')

        try:
            resize_image(image_path, save_path, max_length=max_length, quality=quality)
        except (IOError, ValueError):
            print(f'\tERROR: Encountered error while processing')
            continue

        if verbose:
            size_before, size_after = path.getsize(image_path), path.getsize(save_path)
            percent = (size_after - size_before) / size_before * 100
            print(f'\tDONE: {readable_size(size_before)} -> {readable_size(size_after)} ({percent:.1f}%)')

        processed.append(save_path)
    return processed
