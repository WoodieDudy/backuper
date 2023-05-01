import argparse
import math
import os
import time
import zipfile
import threading
import datetime
from pathlib import Path

from disks import GoogleDisk, YandexDisk

from croniter import croniter

from disks.base_disk import BaseDisk


def _parse_args():
    def path(args_string):
        res_path = Path(args_string)
        if not res_path.exists():
            raise ValueError('This path doesn\'t exist')
        print(res_path)
        return res_path

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

    start_parser.add_argument("-p", "--path", help="", type=path)
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
    # disk.upload(args.path)

    t = threading.Thread(
        target=f,
        args=(disk, args.path, args.rate),
        name="amugs"
    )
    t.start()
    t.name
    t.join()
    f(disk, args.path, args.rate)
    print('done')


def cron_parser(cron):
    now = datetime.datetime.now()
    cron = croniter(cron, now)
    cron.get_next(datetime.datetime)
    next_time = cron.get_next(datetime.datetime)
    return (next_time - now).total_seconds()


def f(disk: BaseDisk, path: Path, cron: str):
    rate = cron_parser(cron)
    print(f'rate is {rate} seconds')

    last_backup_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)  # TODO

    while True:
        if path.is_dir():
            files_iter = list(path.rglob('*'))
        else:
            files_iter = [path]

        files = []

        for file in files_iter:
            last_modification_time = math.ceil(os.path.getmtime(file))
            last_modification_time = datetime.datetime.fromtimestamp(last_modification_time)
            if last_modification_time >= last_backup_time:
                files.append(file)

        if not files:
            print('empty => skip')
            last_backup_time = datetime.datetime.now()
            time.sleep(rate)
            continue

        archive_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{path.name}.zip"
        archive_dir = Path.home() / '.backuper'  # TODO: cd instead concat
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / archive_name

        with zipfile.ZipFile(archive_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for file in files:
                zf.write(file)

        disk.upload(str(archive_path))
        print('work done now wait')
        last_backup_time = datetime.datetime.now()
        time.sleep(rate)
        print('time out new iter')


if __name__ == '__main__':
    main()

# detached_process = subprocess.Popen(
#     [sys.executable, "backup_loop.py", str(path), cron],
#     stdout=subprocess.DEVNULL,
#     stderr=subprocess.DEVNULL,
#     start_new_session=True
# )
