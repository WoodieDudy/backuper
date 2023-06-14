import json
import os
import zipfile
import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Iterable, Optional

from .defs import secrets_file, archives_dir, root_save


def make_app_dirs() -> None:
    """
    Создает необходимые для работы приложения служебные директории
    """
    os.makedirs(root_save, exist_ok=True)
    os.makedirs(archives_dir, exist_ok=True)


def extract_secrets_from_json(disk: str = None) -> dict:
    """
    Извлекает из файла информацию, необходимую для работы приложения
    :param disk: имя диска
    """
    try:
        if os.path.getmtime(secrets_file) < datetime.datetime.now().timestamp() - datetime.timedelta(
                days=10).total_seconds():
            return {}
        with open(secrets_file) as f:
            data: dict = json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        return {}
    if disk is not None:
        return data.get(disk, {})
    return data


def save_secrets(disk: str, secrets: Optional[dict]) -> None:
    """
    Сохраняет в файл информацию, необходимую для работы приложения
    :param disk: имя диска
    :param secrets: секреты для сохранения
    """
    if secrets is None:
        return

    data = extract_secrets_from_json()

    if disk not in data:
        data[disk] = {}

    data[disk].update(secrets)

    with open(secrets_file, "w") as f:
        json.dump(data, f)


def cron_parser(cron_expression):
    """
    Парсит крон для извлечения периодичности бэкапа
    :param cron: значение строки cron
    :return: периодичность в секундах
    """

    cron_parts = cron_expression.split()

    if cron_parts[0] == '*':
        return 60
    elif cron_parts[0].startswith('*/'):
        minutes = int(cron_parts[0][2:])
        return minutes * 60
    elif cron_parts[1] == '*':
        return 60 * 60
    elif cron_parts[1].startswith('*/'):
        hours = int(cron_parts[1][2:])
        return hours * 60 * 60
    else:
        raise ValueError("Unsupported cron format")


def make_archive(root_path: Path, files: list) -> str:
    """
    Собирает архив для загрузки
    :param root_path: путь до директории, откуда производится сжатие
    :param files: список файлов для сэатия
    :return: путь до результирующего архива
    """
    archive_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{root_path.name}.zip"
    archive_path = archives_dir / archive_name
    os.chdir(archives_dir)

    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for full_path in files:
            relative_path = os.path.relpath(full_path, root_path)
            zf.write(full_path, relative_path)

    return str(archive_path)


def get_files_from_path(path: Path) -> set:
    """
    Получает файлы по указанному пути
    :param path: путь, который необходимо распарсить
    :return: множество файлов
    """
    if path.is_dir():
        files_iter = path.rglob("*")
    else:
        files_iter = [path]

    return set(files_iter)


def filter_files_by_time(files: Iterable, last_backup_time: int) -> set:
    """
    Фильтует файлы, убирая те, которые не были изменены
    :param files: список файлов
    :param last_backup_time: временная метка последнего бэкапа
    :return: отфильтрованные файлы
    """
    filtered_files = set()
    for filepath in files:
        last_modification_time = int(os.path.getmtime(filepath))

        if last_modification_time >= last_backup_time:
            filtered_files.add(filepath)

    return filtered_files
