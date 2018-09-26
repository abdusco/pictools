#!/usr/bin/python3
import click
from .filetools import *
from .processors import *
from .separators import *


@click.group(chain=True)
@click.option('--verbose', is_flag=True)
@click.pass_context
def cli(context, verbose):
    context.obj['verbose'] = verbose
    click.echo('running')


@cli.command('separate', help='Separate images according to criterias')
@click.argument('dir', nargs=-1, type=click.Path(file_okay=False, exists=True))
@click.option('--by', type=click.Choice(['orientation', 'segment']))
@click.option('--out', default='./')
@click.pass_context
def separate(context, dir, by, out):
    verbose = context.obj.get('verbose')
    for d in dir:
        if by == 'orientation':
            click.echo(f'Separating images in {d} by image orientation')
            images = find_images(d, recursive=False)
            separate_by_orientation(images, out=out, verbose=verbose)
        elif by == 'segment':
            click.echo(f'Separating images in {d} by first segment')
            images = find_images(d, recursive=False)
            separate_by_first_segment(images, out=out, verbose=verbose)


@cli.command('process', help='Process images in folders')
@click.argument('dirs', nargs=-1)
@click.option('--max-length', default=5000, help='Max image side length in pixels')
@click.option('--quality', default=80)
@click.option('--zip', is_flag=True, help='Create zip file from processed files')
@click.option('--force', is_flag=True, help='Force reprocess all files')
@click.option('--prefix', default='r__', help='Add prefix to processed images')
@click.option('--suffix', default='', help='Add suffix to processed images')
@click.option('--pattern', is_flag=True, help='Search by regex')
@click.pass_context
def process(context, dirs, max_length, quality, force, zip, prefix, suffix, pattern):
    verbose = context.obj.get('verbose')

    matches = []
    for item in dirs:
        if pattern:
            matches += find_dirs_by_regex(parent='.', pattern=item)
        else:
            if not path.exists(item):
                continue
            matches += [path.abspath(item)]

    if not matches:
        click.echo('Nothing matched')
        raise click.Abort

    click.echo(f'Matched dirs: {len(matches)}')
    for item in matches:
        click.echo(f'\t{item}')

    if not click.confirm('Proceed?'):
        raise click.Abort

    for d in matches:
        print(f'Processing {d}')
        images = find_images(d, recursive=True)
        if not images:
            print(f'No images in {d}')
            continue
        processed = process_images(images,
                                   quality=quality,
                                   max_length=max_length,
                                   prefix=prefix,
                                   suffix=suffix,
                                   force=force,
                                   verbose=verbose)
        if zip:
            zip_path = path.join(d, path.basename(d) + '.zip')
            zip_files(processed,
                      zip_path=zip_path,
                      flat=True)
            click.echo(f'Saved zip file to {zip_path}')


@cli.command('rename', help='Rename images in folders')
@click.argument('dirs', nargs=-1)
@click.option('--pattern', is_flag=True, help='Search by regex')
@click.pass_context
def rename(context, dirs, pattern):
    matches = []
    for item in dirs:
        if pattern:
            matches += find_dirs_by_regex(parent='.', pattern=item)
        else:
            if not path.exists(item):
                continue
            matches += [path.abspath(item)]

    if not matches:
        click.echo('Nothing matched')
        raise click.Abort

    click.echo(f'Matched dirs: {len(matches)}')
    for item in matches:
        click.echo(f'\t{item}')

    if not click.confirm('Proceed?'):
        raise click.Abort

    for d in matches:
        numerate_images_in_dir(d)


if __name__ == '__main__':
    cli(obj={})
