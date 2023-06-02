import os
import signal
import datetime
import time
from pathlib import Path
import logging

from backuper import _parse_args
from disks.base_disk import BaseDisk
from disks.google_disk import GoogleDisk
from disks.yandex_disk import YandexDisk
from utils import get_running_processes, save_processes_info, cron_parser, extract_secrets_from_json, make_archive

logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="w",
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def get_disk(name: str) -> BaseDisk:
    if name == "yandex":
        return YandexDisk()
    elif name == "google":
        return GoogleDisk()
    else:
        raise ValueError("Invalid disk name")


def start_process(name: str, path: Path, cron: str, disk_name: str):
    logging.info(f"Start process {name} with path {path} and cron {cron}")

    running_processes = get_running_processes()
    if name in running_processes:
        try:
            os.kill(running_processes[name]['pid'], signal.SIGTERM)
        except ProcessLookupError:
            pass

    disk = get_disk(disk_name)
    disk.load_secrets()

    logging.info(f"Autorized in {disk_name} disk")
    running_processes[name] = {
        "cron": cron,
        "pid": os.getpid(),
        "path": str(path),
    }

    save_processes_info(running_processes)
    print(f"Background process started with PID {os.getpid()}")

    rate = cron_parser(cron)
    last_backup_time = 0

    logging.info(f"Start backup with rate {rate}")
    while True:

        last_backup_time, archive_path, is_empty = make_archive(path, last_backup_time)
        logging.info(f"last_backup_time: {last_backup_time}, archive_path: {archive_path}, is_empty: {is_empty}")
        if is_empty:
            logging.info(f"empty, sleeping for {rate} seconds")
            time.sleep(rate)
            continue
        else:
            logging.info(f"File size: {os.path.getsize(archive_path) / (1024 ** 3):.2f}G")

        logging.info("Start upload")
        disk.upload(archive_path)
        logging.info("work done now wait")
        last_backup_time = datetime.datetime.now().timestamp()
        time.sleep(rate)
        logging.info("time out new iter")


if __name__ == '__main__':
    args = _parse_args()
    try:
        start_process(args.name, args.path, args.cron, args.disk)
    except Exception as e:
        # tb = traceback.format_exc()
        logging.exception(e)
