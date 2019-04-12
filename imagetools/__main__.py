from pathlib import Path
import sys
from argparse import ArgumentParser

from imagetools import fs
from imagetools.images import process_dir
from loguru import logger


def get_args() -> tuple:
    parser = ArgumentParser('pictools')
    parser.add_argument('--max-length', '--max', action='store', default=5000, type=int,
                        help='Max side length of processed images. Default: 5000')
    parser.add_argument('--quality', '-q', action='store', default=75, type=int, help='JPEG save quality. Default: 75')
    parser.add_argument('--glob', '-g', action='store_true', help='Search dirs by glob')
    parser.add_argument('--regex', '-r', action='store_true', help='Search dirs by regex')
    parser.add_argument('--force', '-f', action='store_true', help='Force process images')
    parser.add_argument('--delete', action='store_true', help='Delete completed')
    parser.add_argument('-y', dest='skip_confirmation', action='store_true', help='Skip confirmation')
    parser.add_argument('dirs', nargs='+')
    args = parser.parse_args()

    if args.glob and args.regex:
        raise ValueError('Use only regex or glob')

    return args, parser


def main() -> None:
    args, parser = get_args()

    dirs = []
    if args.glob:
        for glob in args.dirs:
            dirs += fs.find_dirs_by_glob(Path(), glob)
    elif args.regex:
        for pattern in args.dirs:
            dirs += fs.find_dirs_by_regex(Path(), pattern)
    else:
        dirs = [Path(d) for d in args.dirs[1:]]

    if not dirs:
        print(f'No matches for {args.dirs}')
        return

    print('Matches:')
    for d in dirs:
        print(d)
    if not args.skip_confirmation and 'y' != input('Continue? y/n?').strip().lower():
        return

    workdir = Path('_pictools')
    workdir.mkdir(exist_ok=True)

    for d in dirs:
        logger.info(f'Processing {d.stem}')
        target_dir = workdir / d.stem
        target_dir.mkdir(exist_ok=True)
        compressed = process_dir(source_dir=d,
                                 target_dir=target_dir,
                                 max_length=args.max_length,
                                 quality=args.quality,
                                 force=args.force)

        if compressed:
            zip_path = workdir / f'{d.stem}.zip'
            fs.zip(compressed, zip_path)
            logger.success(f'Done: {d}. Saved zip at {zip_path}')

    if args.delete:
        print('All completed. Delete?')
        for d in dirs:
            print(d)
        if 'y' != input('Delete? y/n?').strip().lower():
            for d in dirs:
                d.unlink()


if __name__ == '__main__':
    main()
