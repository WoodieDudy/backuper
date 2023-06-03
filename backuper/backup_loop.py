import os
import signal
import datetime
import time
from pathlib import Path
import logging

from backuper.backup import _parse_args
from backuper.disk_utils import get_disk
from backuper.utils import *

logging.basicConfig(level=logging.INFO, filename="/Users/georgy/Trash/logs.txt", filemode="w",
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def start_process(name: str, path: Path, cron: str, disk_name: str) -> None:
    """
    Запускает отдельный процесс для бэкапа

    :param name: имя для процесса
    :param path: путь файла для бэкапа
    :param cron: периодичность в формате крон
    :param disk_name: название хранилища
    """
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
    backuped_files = set()

    logging.info(f"Start backup with rate {rate}")
    while True:
        files_in_path = get_files_from_path(path)
        new_files = files_in_path - backuped_files

        updated_files = filter_files_by_time(files_in_path, last_backup_time)
        files_to_archive = updated_files | new_files
        if not files_to_archive:
            logging.info(f"empty, sleeping for {rate} seconds")
            time.sleep(rate)
            continue
        backuped_files |= files_to_archive

        archive_path = make_archive(path, files_to_archive)
        logging.info(f"File size: {os.path.getsize(archive_path) / (1024 ** 3):.2f}G")

        logging.info("Start upload")
        disk.upload(archive_path)
        logging.info(f"file uploaded, sleeping for {rate} seconds")
        last_backup_time = datetime.datetime.now().timestamp()
        time.sleep(rate)
        logging.info("time out new iter")


if __name__ == '__main__':
    logging.info("Start backup loop")
    try:
        args = _parse_args()
        logging.info(args)
        start_process(args.name, args.path, args.cron, args.disk)
    except Exception as e:
        logging.exception(e)
