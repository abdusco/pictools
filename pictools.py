#!/usr/bin/python3
import click
from filetools import *
from processors import *
from separators import *


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
@click.argument('dir', nargs=-1, type=click.Path(file_okay=False, exists=True, resolve_path=True))
@click.option('--max-length', default=5000, help='Max image side length in pixels')
@click.option('--quality', default=80)
@click.option('--zip', is_flag=True, help='Create zip file from processed files')
@click.option('--force', is_flag=True, help='Force reprocess all files')
@click.option('--prefix', default='r__', help='Add prefix to processed images')
@click.option('--suffix', default='', help='Add suffix to processed images')
@click.option('--out', default='./')
@click.pass_context
def process(context, dir, max_length, quality, force, zip, prefix, suffix, out):
    verbose = context.obj.get('verbose')
    for d in dir:
        images = find_images(d, recursive=True)
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


if __name__ == '__main__':
    cli(obj={})
