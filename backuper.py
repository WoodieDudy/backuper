import argparse
import os

from disks import GoogleDisk, YandexDisk

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

    args = parser.parse_args()
    return args


def main():
    args = _parse_args()

    if args.disk == 'yandex':
        disk = YandexDisk()
    elif args.disk == 'google':
        disk = GoogleDisk()
    else:
        disk = YandexDisk()

    disk.try_auth()
    disk.upload(args.folder)
    print('done')


if __name__ == '__main__':
    main()
