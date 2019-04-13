from PIL import Image
from pathlib import Path

import typing
from loguru import logger

# suppress compression bomb warnings
Image.MAX_IMAGE_PIXELS *= 10


def resize_image(source: Path, target: Path, quality: int, max_length: int, callback: typing.Callable = None):
    with Image.open(source) as image:
        scale = max_length / max(image.size)
        if scale < 1:
            size = tuple(int(d * scale) for d in image.size)
            image = image.resize(size, Image.LANCZOS)
        try:
            image.save(target, quality=quality, mode='JPEG')
            if callback:
                callback()
        except IOError:
            logger.exception(f'Cannot save: {target}')
    pass
