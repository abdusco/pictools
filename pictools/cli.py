import time
import shutil
import typing
import zipfile
from functools import partial
from pathlib import Path

import click
import loguru

from pictools import fs
from pictools import images


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

    for processor in processors:
        dirs = processor(dirs)
    for _ in dirs:
        pass


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
    def compressor(dirs: typing.Iterator[Path]):
        for d in dirs:
            save_dir: Path = Path(target) / d.name
            save_dir.mkdir(exist_ok=True, parents=True)
            print(click.style(f'Processing: {d}', fg='yellow'))
            with click.progressbar(fs.find_images(d)) as bar:
                def update_bar(before: Path, after: Path):
                    before_bytes, after_bytes = [f.stat().st_size for f in [before, after]]
                    before_size, after_size = [fs.readable_size(s) for s in [before_bytes, after_bytes]]
                    change_percent = (after_bytes - before_bytes) / before_bytes * 100

                    name = click.style(before.name, fg="yellow")
                    report = f'{before_size} -> {after_size} [{change_percent:.0f}%]'
                    bar.label = f'{name}: {report}'

            for f in bar:
                save_path: Path = save_dir / f.name
                if not force and save_path.exists():
                    time.sleep(0.1)
                    update_bar(f, save_path)
                    continue

                images.resize_image(source=f,
                                    target=save_path,
                                    quality=quality,
                                    max_length=max_length,
                                    callback=partial(update_bar, f, save_path))
            yield save_dir

    return compressor


@cli.command('zip',
             help='Pack directories')
@click.option('-o', '--out', 'target',
              default='_pictools',
              help='Location to save zip files')
def zip_files(target: str):
    def zipper(dirs: typing.Iterator[Path]):
        target_dir = Path(target)
        target_dir.mkdir(exist_ok=True)
        for d in dirs:
            save_path: Path = target_dir / f'{d.name}.zip'
            print(click.style(f'Zipping: {d}', fg='magenta'))
            with zipfile.ZipFile(save_path, 'w') as z, click.progressbar(list(d.iterdir())) as bar:
                for f in bar:
                    bar.label = f.name
                    z.write(f, arcname=f.name)
                    time.sleep(0.1)
            yield d

    return zipper


@cli.command('flatten',
             help='Flatten folder hierarchy')
@click.option('-s', '--separator',
              default='~',
              help='Separator character')
def flatten(separator: str):
    def flattener(dirs: typing.Iterator[Path]):
        for d in dirs:
            print(click.style(f'Flattening {d}', fg='red'))
            with click.progressbar(list(d.glob('**/*'))) as bar:
                for f in bar:
                    if f.is_dir():
                        continue
                    flattened = str(f.relative_to(d)).replace('/', separator)
                    f.rename(d / flattened)
                    bar.label = f.name
                for d in d.glob('**/*/'):
                    if d.is_dir():
                        shutil.rmtree(d)
            yield d

    return flattener


@cli.command('delete', help='Delete directories')
def delete():
    def deleter(dirs: typing.Iterator[Path]):
        with click.progressbar(dirs) as bar:
            for d in bar:
                bar.label = f'Deleting: {d.name}'
                time.sleep(1)
                shutil.rmtree(d, ignore_errors=True)
                yield d

    return deleter


if __name__ == '__main__':
    cli()
