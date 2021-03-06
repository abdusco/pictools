import time
import shutil
import typing
import zipfile
from collections import namedtuple
from dataclasses import dataclass
from functools import partial
from pathlib import Path

import click
import loguru

from pictools import fs
from pictools import images


@dataclass
class Job:
    original_dir: Path
    processed_dir: Path = None


progressbar = partial(click.progressbar,
                      item_show_func=lambda item: item.stem if item else '',
                      width=20)


@click.group(name='pictools',
             chain=True)
@click.option('-y', '--yes', is_flag=True)
@click.option('-d', '--dir', 'dirs',
              multiple=True,
              help='Use directory')
@click.option('-g', '--glob', 'globs',
              multiple=True,
              help='Find directories by glob')
@click.option('-r', '--regex', 'patterns',
              multiple=True,
              help='Find directories by regex pattern')
def cli(dirs: typing.Tuple[str],
        globs: typing.Tuple[str],
        patterns: typing.Tuple[str],
        yes: bool):
    pass


@cli.resultcallback()
def pipeline(processors,
             dirs: typing.Tuple[str],
             globs: typing.Tuple[str],
             patterns: typing.Tuple[str],
             yes: bool):
    dirs = fs.find_dirs(dirs=dirs, globs=globs, patterns=patterns)
    if not dirs:
        print('No matches')
        raise click.Abort

    print(click.style('Found:', fg='green'))
    for d in dirs:
        print(d)

    if not yes and not click.confirm('Continue?', abort=True):
        pass
    dirs = [Job(original_dir=d) for d in dirs]
    for processor in processors:
        dirs = processor(dirs)
    for d in dirs:
        print(f'Done: {d}')


@cli.command('resize',
             help='Process and compress images')
@click.option('-q', '--quality',
              default=75,
              type=int)
@click.option('-m', '-l', '--max-length',
              default=5000,
              type=int)
@click.option('-o', '--out', 'target',
              default='_pictools',
              help='Location to save zip files')
@click.option('-f', '--force',
              is_flag=True)
def resize_images(quality: int, max_length: int, target: str, force: bool):
    @loguru.logger.catch()
    def resizer(jobs: typing.Iterator[Job]):
        for j in jobs:
            save_dir: Path = Path(target) / j.original_dir.name
            save_dir.mkdir(exist_ok=True, parents=True)
            with progressbar(fs.find_images(j.original_dir), label='Resizing') as bar:
                for f in bar:
                    save_path: Path = save_dir / f.name
                    if not force and save_path.exists():
                        continue
                    images.resize_image(source=f,
                                        target=save_path,
                                        quality=quality,
                                        max_length=max_length)
            j.processed_dir = save_dir
            yield j

    return resizer


@cli.command('zip',
             help='Pack directories')
@click.option('-o', '--out', 'target',
              default='_pictools',
              help='Location to save zip files')
def zip_files(target: str):
    def zipper(jobs: typing.Iterator[Job]):
        target_dir = Path(target)
        target_dir.mkdir(exist_ok=True)
        for j in jobs:
            save_path: Path = target_dir / f'{j.processed_dir.name}.zip'
            with zipfile.ZipFile(save_path, 'w') as z, progressbar(list(j.processed_dir.iterdir()),
                                                                   label='Zipping') as bar:
                for f in bar:
                    z.write(f, arcname=f.name)
            j.processed_dir
            yield j

    return zipper


@cli.command('flatten',
             help='Flatten folder hierarchy')
@click.option('-s', '--separator',
              default='~',
              help='Separator character')
def flatten(separator: str):
    def flattener(dirs: typing.Iterator[Path]):
        for d in dirs:
            with progressbar(list(d.glob('**/*')), label='Flattening') as bar:
                for f in bar:
                    if f.is_dir():
                        continue
                    flattened = str(f.relative_to(d)).replace('/', separator)
                    f.rename(d / flattened)
                for d in d.glob('**/*/'):
                    if d.is_dir():
                        shutil.rmtree(d)
            yield d

    return flattener


@cli.command('delete', help='Delete directories')
def delete():
    def deleter(dirs: typing.Iterator[Path]):
        with progressbar(dirs, label='Deleting') as bar:
            for d in bar:
                time.sleep(1)
                shutil.rmtree(d, ignore_errors=True)
                yield d

    return deleter


if __name__ == '__main__':
    cli()
