import os
import signal
import datetime
import time
import traceback
import zipfile
from pathlib import Path

from backuper import _parse_args
from disks import YandexDisk, GoogleDisk
from logger import Logger
from utils import get_running_processes, save_processes_info, cron_parser


def start_process(name: str, path: Path, cron: str, disk_name: str):
    logger = Logger('logs.txt')
    logger.log(f"Start process {name} with path {path} and cron {cron}")

    running_processes = get_running_processes()
    if name in running_processes:
        try:
            os.kill(running_processes[name]['pid'], signal.SIGTERM)
        except ProcessLookupError:
            pass

    if disk_name == 'yandex':
        disk = YandexDisk()
    elif disk_name == 'google':
        disk = GoogleDisk()
    else:
        disk = YandexDisk()

    disk.try_auth()

    logger.log(f"Autorized in {disk_name} disk")
    running_processes[name] = {
        'cron': cron,
        'pid': os.getpid(),
        'path': str(path),
    }

    save_processes_info(running_processes)
    print(f"Background process started with PID {os.getpid()}")

    rate = cron_parser(cron)
    last_backup_time = datetime.datetime.min

    logger.log(f"Start backup with rate {rate}")
    while True:
        if path.is_dir():
            files_iter = path.rglob('*')
        else:
            files_iter = [path]

        files = []
        for file in files_iter:
            last_modification_time = int(os.path.getmtime(file))
            last_modification_time = datetime.datetime.fromtimestamp(last_modification_time)
            if last_modification_time >= last_backup_time:
                files.append(file.name)

        if not files:
            print('empty => skip')
            last_backup_time = datetime.datetime.now()
            time.sleep(rate)
            continue

        archive_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{path.name}.zip"
        archive_dir = Path.home() / '.backuper'
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / archive_name
        os.chdir(path.parent)

        with zipfile.ZipFile(archive_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for full_path in files:
                relative_path = os.path.relpath(full_path, path)
                zf.write(relative_path)

        disk.upload(archive_path)
        logger.log('work done now wait')
        last_backup_time = datetime.datetime.now()
        time.sleep(rate)
        logger.log('time out new iter')


if __name__ == '__main__':
    args = _parse_args()
    logger = Logger('logs.txt')
    try:
        start_process(args.name, args.path, args.cron, args.disk)
    except Exception as e:
        tb = traceback.format_exc()
        logger.log(f"Error: {tb}")
