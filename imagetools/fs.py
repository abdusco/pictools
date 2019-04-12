import re
import zipfile
from pathlib import Path
import typing
from loguru import logger


def find_dirs_by_regex(parent_dir: Path, pattern: str) -> typing.List[Path]:
    pattern = re.compile(pattern=pattern, flags=re.IGNORECASE | re.UNICODE)
    return [item
            for item in parent_dir.glob('*/')
            if item.is_dir() and pattern.search(item.name)]


def find_dirs_by_glob(parent_dir: Path, glob: str) -> typing.List[Path]:
    return [item
            for item in parent_dir.glob(glob)
            if item.is_dir()]


def find_images(parent_dir: Path, criteria: callable = None, sort=True) -> typing.List[Path]:
    images = []
    extensions = ['.jpg', '.jpeg']
    for item in parent_dir.glob('**/*'):
        if not any(ext for ext in extensions if item.suffix == ext):
            continue
        if criteria and not criteria(item):
            continue
        images.append(item)
    if sort:
        images = sorted(images)
    return images


def zip(files: typing.List[Path], save_path: Path):
    with zipfile.ZipFile(save_path, 'w') as z:
        for f in files:
            z.write(f, f.name)


def readable_size(bytes: int, decimal_places: int = 2) -> str:
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            break
        bytes /= 1024.0
    return f'{bytes:.{decimal_places}f}{unit}'
