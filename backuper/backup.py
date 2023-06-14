import argparse
import subprocess
import sys

from pkg_resources import resource_filename

from backuper.defs import processes_info_file
from backuper.processes_repository import ProcessesRepository
from .disk_utils import get_disk, is_disk_authed
from .utils import *


def _parse_args():  # pragma: no cover
    def path(args_string):
        res_path = Path(args_string)
        if not res_path.exists():
            raise ValueError("This path doesn't exist")
        return res_path

    def cron(args_string):
        try:
            cron_parser(args_string)
            return args_string
        except ValueError:
            raise ValueError("Invalid cron format")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    start_parser = subparsers.add_parser("start")
    start_parser.set_defaults(cmd="start")
    start_parser.add_argument("-p", "--path", help="path to file", type=path)
    start_parser.add_argument("-c", "--cron", help="backuper rate", type=cron)
    start_parser.add_argument("-d", "--disk", help="[google, yandex]", choices=["yandex", "google"])
    start_parser.add_argument("-n", "--name", help="name of process", type=str)

    stop_parser = subparsers.add_parser('stop')
    stop_parser.set_defaults(cmd='stop')
    stop_parser.add_argument("-n", "--name", help="name of process", type=str)

    auth_parser = subparsers.add_parser('auth')
    auth_parser.set_defaults(cmd='auth')
    auth_parser.add_argument("-d", "--disk", help="[google, yandex]", choices=["yandex", "google"])

    list_parser = subparsers.add_parser('backups')
    list_parser.set_defaults(cmd="backups")

    files_parser = subparsers.add_parser("diskfiles")
    files_parser.set_defaults(cmd="diskfiles")
    files_parser.add_argument("-d", "--disk", help="[google, yandex]", choices=["yandex", "google"])

    download_parser = subparsers.add_parser("download")
    download_parser.set_defaults(cmd="download")
    download_parser.add_argument("-d", "--disk", help="[google, yandex]", choices=["yandex", "google"])
    download_parser.add_argument("-n", "--name", help="name of file from disk", type=str)

    args = parser.parse_args()
    return args


def start_backup(disk: str, cron: str, process_name: str, path: str) -> None:
    """
    Запускает процесс бэкапа в хранилище

    :param disk: хранилище для загрузки файла
    :param cron: периодичность в формате
    :param process_name: имя, которое мы даём процессу
    :param path: путь к файлу, который мы хотим бэкапить
    """
    if not is_disk_authed(get_disk(disk).__name__):
        print("You're not authorized in disk")
        print("Please, run 'python backup.py auth -d <disk>")
        return

    print("start")
    backup_loop_path = resource_filename('backuper', 'backup_loop.py')
    new_process = subprocess.Popen(
        [
            sys.executable, backup_loop_path, "start", "-p", str(path),
            "-c", cron, "-d", disk, "-n", process_name
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    print(new_process.pid)


def stop_backup(name: str) -> None:
    """
    Останавливает процесс периодического создания бэкапов

    :param name: имя процесса, который нужно остановить
    """
    processes_repository = ProcessesRepository(processes_info_file)
    processes_repository.stop_process(name)


def get_backups() -> None:
    """
    Печатает список запущенных фоновых бэкапов
    """
    processes_repository = ProcessesRepository(processes_info_file)

    running_processes = processes_repository.load()
    if not running_processes:
        print("No running processes")
        return

    for name, info in running_processes.items():
        print(name)
        for key, value in info.items():
            print(f"\t{key}: {value}")


def auth(disk: str) -> None:
    """
    Авторизация в диске с сохранением данных авторизации в конфигурационный файл для дальнейшей работы с диском

    :param disk: хранилище, в котором планируется авторизоваться
    """
    get_disk(disk)()


def get_files_from_disk(disk: str):
    """
    Получение списка всех бэкапов, находящихся на хранилище

    :param disk: хранилище, из которого нужно получить список
    """
    disk = get_disk(disk)()
    for file in disk.list_of_files():
        print(file)


def download_file_from_disk(disk: str, name: str) -> None:
    """
    Скачивание файла из хранилища

    :param disk: хранилище, с которого планируется скачивать файл
    :param name: имя файла для скачивания
    """

    disk = get_disk(disk)()
    try:
        disk.download(name)
    except ValueError:
        print("No such file on disk")


def main():  # pragma: no cover
    args = _parse_args()
    make_app_dirs()

    if args.cmd == "start":
        start_backup(args.disk, args.cron, args.name, args.path)

    elif args.cmd == 'stop':
        stop_backup(args.name)

    elif args.cmd == "backups":
        get_backups()

    elif args.cmd == "auth":
        auth(args.disk)

    elif args.cmd == "diskfiles":
        get_files_from_disk(args.disk)

    elif args.cmd == "download":
        download_file_from_disk(args.disk, args.name)

    else:
        raise ValueError("Unknown command")


if __name__ == "__main__":
    main()
