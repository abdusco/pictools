from PIL import Image
from pathlib import Path

from imagetools import fs
from imagetools.fs import find_images
import typing
from loguru import logger

# suppress compression bomb warnings
Image.MAX_IMAGE_PIXELS *= 10


def process_dir(source_dir: Path, target_dir: Path, max_length: int, quality: int, force=False) -> typing.List[Path]:
    images = find_images(parent_dir=source_dir)
    if not images:
        logger.warning(f'No images in {source_dir}')
        return []

    processed = []
    for img in images:
        logger.info(f'Processing: {img.name}')

        save_path: Path = target_dir / f'{img.stem}_max{max_length}q{quality}{img.suffix}'
        if not force and save_path.exists():
            logger.info(f'Done: {img}')
            continue

        with Image.open(img) as image:
            scale = max_length / max(image.size)
            if scale < 1:
                size = tuple(int(d * scale) for d in image.size)
                image = image.resize(size, Image.LANCZOS)
            try:
                image.save(save_path, quality=quality, mode='JPEG')
            except IOError:
                logger.exception(f'Cannot save: {save_path}')
        processed.append(save_path)

        before_bytes, after_bytes = [f.stat().st_size for f in [img, save_path]]
        before_size, after_size = [fs.readable_size(s) for s in [before_bytes, after_bytes]]
        change_percent = (after_bytes - before_bytes) / before_bytes * 100
        logger.success(f'Done: {before_size} -> {after_size} ({change_percent:.0f}%)')

    return processed
