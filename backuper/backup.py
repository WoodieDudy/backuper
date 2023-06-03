import argparse
import signal
import subprocess
import sys
from pkg_resources import resource_filename

from .disk_utils import get_disk
from .disks.yandex_disk import YandexDisk
from .utils import *


def _parse_args():
    def path(args_string):
        res_path = Path(args_string)
        if not res_path.exists():
            raise ValueError("This path doesn't exist")
        print(res_path)
        return res_path

    def cron(args_string):
        if not croniter.is_valid(args_string):
            raise ValueError("Invalid cron format")
        return args_string

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


def disk_authed(disk_name: str) -> bool:
    """
    Проверка, авторизован ли пользователь в диске

    :param disk_name: название хранилища для проверки
    :return: True, если да; False, если нет.
    """
    if extract_secrets_from_json(disk_name):
        return True
    return False


def auth_yandex_disk() -> dict:
    """
    Авторизация в яндекс диске

    :return: словарь с токеном доступа
    """
    ya_disk = YandexDisk()
    ya_disk.try_auth()
    secret = ya_disk.disk.token
    return {"access_token": secret}


def start_backup(disk: str, cron: str, process_name: str, path: str) -> None:
    """
    Запускает процесс бэкапа в хранилище

    :param disk: хранилище для загрузки файла
    :param cron: периодичность в формате
    :param process_name: имя, которое мы даём процессу
    :param path: путь к файлу, который мы хотим бэкапить
    """
    if not disk_authed(disk):
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
        start_new_session=True  # TODO мб не создавать два раза
    )
    print(new_process.pid)


def stop_backup(name: str) -> None:
    """
    Останавливает процесс периодического создания бэкапов

    :param name: имя процесса, который нужно остановить
    """
    running_processes = get_running_processes()
    if name not in running_processes:
        print(f"Error: Process {name} not found")
        return
    pid = running_processes[name]["pid"]
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Background process with PID {pid} stopped.")
        del running_processes[name]
    except OSError:
        print(f"Error: Unable to stop process with PID {pid}")
    save_processes_info(running_processes)


def get_backups() -> None:
    running_processes = get_running_processes()
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
    if disk == "yandex":
        secret_data = auth_yandex_disk()
    elif disk == "google":
        secret_data = {}

    save_secrets(disk, secret_data)


def get_files_from_disk(disk: str):
    """
    Получение списка всех бэкапов, находящихся на хранилище

    :param disk: хранилище, из которого нужно получить список
    """
    disk = get_disk(disk)
    disk.load_secrets()
    for file in disk.list_of_files():
        print(file)


def download_file_from_disk(disk: str, name: str) -> None:
    """
    Скачивание файла из хранилища

    :param disk: хранилище, с которого планируется скачивать файл
    :param name: имя файла для скачивания
    """

    disk = get_disk(disk)
    disk.load_secrets()
    try:
        disk.download(name)
    except ValueError:
        print("No such file on disk")


def main():
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
