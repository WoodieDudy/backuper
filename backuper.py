import argparse
import os
import pathlib
from datetime import datetime
from time import sleep
import shutil

from croniter import croniter


def _parse_args():
    def folder(args_string):
        if not os.path.exists(args_string):
            raise ValueError('This path doesn\'t exist')
        return args_string

    def rate(args_string):
        if not croniter.is_valid(args_string):
            raise ValueError("Invalid cron format")
        return args_string

    def disk(args_string):
        if args_string not in ['yandex', 'google']:
            raise ValueError('Possible choices: [yandex, google]')
        return args_string

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    start_parser = subparsers.add_parser('start')
    stop_parser = subparsers.add_parser('stop')
    start_parser.set_defaults(cmd='start')
    stop_parser.set_defaults(cmd='stop')

    start_parser.add_argument("-f", "--folder", help="", type=folder)
    start_parser.add_argument("-r", "--rate", help="rate cron", type=rate)
    start_parser.add_argument("-d", "--disk", help="[google, yandex]", type=disk)
    start_parser.add_argument("-t", "--token", help="", type=str)

    args = parser.parse_args()
    return args


def backup(file_path: pathlib.Path):
    # once per minute create duplicate of file with timestamp
    while True:
        file_name_without_ext = os.path.splitext(file_path.name)[0]
        new_path = file_path.parent.joinpath(file_name_without_ext + f"{datetime.now()}" + file_path.suffix)
        shutil.copyfile(file_path, new_path)
        print(new_path)
        sleep(60)


def main():
    args = _parse_args()
    print(args)
    backup(pathlib.Path('test.txt'))


if __name__ == '__main__':
    main()
