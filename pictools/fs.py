import itertools
import re
import zipfile
from pathlib import Path
import typing


def find_dirs(dirs: typing.Tuple[str],
              globs: typing.Tuple[str],
              patterns: typing.Tuple[str]) -> typing.List[Path]:
    found = []

    for d in dirs:
        dir = Path(d)
        if dir.exists() and dir.is_dir():
            found.append(dir)
    for p in patterns:
        pattern = re.compile(p, flags=re.IGNORECASE)
        for item in Path().iterdir():
            if item.is_dir() and pattern.search(item.name):
                found.append(item)
    for g in globs:
        for item in Path().glob(g):
            if item.is_dir():
                found.append(item)

    return found


def find_images(parent_dir: Path, criteria: callable = None, sort=True) -> typing.List[Path]:
    images = []
    extensions = ['jpg', 'jpeg']

    for item in itertools.chain(*(parent_dir.glob(f'**/*.{ext}') for ext in extensions)):
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
