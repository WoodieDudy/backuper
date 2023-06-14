import time
import logging

from backuper.archive_maker import ArchiveMaker
from backuper.backup import _parse_args
from backuper.controller import Controller, InfiniteController
from backuper.disk_utils import get_disk
from backuper.disks.base_disk import BaseDisk
from backuper.processes_repository import ProcessesRepository
from backuper.utils import *
from backuper.defs import logs_file, processes_info_file

logging.basicConfig(level=logging.INFO, filename=logs_file, filemode="w",
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def start_process(
        name: str, path: Path, cron: str,
        disk: BaseDisk, backup_controller: Controller,
        processes_repository: ProcessesRepository
) -> None:
    """
    Запускает отдельный процесс для бэкапа

    :param disk:
    :param name: имя для процесса
    :param path: путь файла для бэкапа
    :param cron: периодичность в формате крон
    :param disk_name: название хранилища
    """

    logging.info(f"Start process {name} with path {path} and cron {cron}")

    if name in processes_repository:
        processes_repository.stop_process(name)

    processes_repository.add_process(name, {
        "cron": cron,
        "pid": os.getpid(),
        "path": str(path),
    })

    archive_maker = ArchiveMaker(path)
    rate = cron_parser(cron)

    logging.info(f"Start backup with rate {rate}")
    while backup_controller.should_continue():
        archive_path = archive_maker.make_fresh_archive()
        if archive_path is None:
            print(archive_path)
            time.sleep(rate)
            continue
        disk.upload(archive_path)
        time.sleep(rate)


if __name__ == '__main__':  # pragma: no cover
    logging.info("Start backup loop")
    try:
        args = _parse_args()
        logging.info(args)
        disk = get_disk(args.disk)()
        logging.info(f"Authorized in {disk} disk")
        processes_repository = ProcessesRepository(processes_info_file)
        controller = InfiniteController()
        start_process(args.name, args.path, args.cron, disk, controller, processes_repository)
    except Exception as e:
        logging.exception(e)
