import json
import os
import zipfile
import datetime
from pathlib import Path

from croniter import croniter

from .defs import processes_info_file, secrets_file, archives_dir, root_save


def make_app_dirs():
    os.makedirs(root_save, exist_ok=True)
    os.makedirs(archives_dir, exist_ok=True)


def get_running_processes() -> dict:
    try:
        with open(processes_info_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}
    return data


def save_processes_info(data: dict):
    with open(processes_info_file, "w") as f:
        json.dump(data, f)


def extract_secrets_from_json(disk: str = None):
    try:
        if os.path.getmtime(secrets_file) < datetime.datetime.now().timestamp() - datetime.timedelta(days=10).total_seconds():
            return {}
        with open(secrets_file) as f:
            data: dict = json.load(f)
    except FileNotFoundError:
        return {}
    if disk is not None:
        return data.get(disk, {})
    return data


def save_secrets(disk: str, secrets: dict):
    data = extract_secrets_from_json()
    if disk not in data:
        data[disk] = {}
    data[disk].update(secrets)
    with open(secrets_file, "w") as f:
        json.dump(data, f)


def cron_parser(cron):
    now = datetime.datetime.now()
    cron = croniter(cron, now)
    cron.get_next(datetime.datetime)
    next_time = cron.get_next(datetime.datetime)
    return (next_time - now).total_seconds()


def make_archive(root_path: Path, files: list) -> str:
    archive_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{root_path.name}.zip"
    archive_path = archives_dir / archive_name
    os.chdir(archives_dir)

    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for full_path in files:
            relative_path = os.path.relpath(full_path, root_path)
            zf.write(full_path, relative_path)

    return str(archive_path)


def get_files_from_path(path: Path):
    if path.is_dir():
        files_iter = path.rglob("*")
    else:
        files_iter = [path]

    return set(files_iter)


def filter_files_by_time(files: list, last_backup_time: int):
    filtered_files = set()
    for filepath in files:
        last_modification_time = int(os.path.getmtime(filepath))

        if last_modification_time >= last_backup_time:
            filtered_files.add(filepath)

    return filtered_files
