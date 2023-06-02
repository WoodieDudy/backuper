import json
import os
import zipfile
import datetime
from pathlib import Path

from croniter import croniter


processes_info_file = "processes.json"
secrets_file = "secrets.json"


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


def extract_secrets_from_json(disk: str):
    try:
        if os.path.getmtime(secrets_file) < datetime.datetime.now().timestamp() - datetime.timedelta(days=10).total_seconds():
            return {}
        with open(secrets_file) as f:
            data: dict = json.load(f)
    except FileNotFoundError:
        return {}
    return data.get(disk, {})


def save_secrets(disk: str, secrets: dict):
    data = extract_secrets_from_json(disk)
    data[disk] = secrets
    with open(secrets_file, "w") as f:
        json.dump(data, f)


def cron_parser(cron):
    now = datetime.datetime.now()
    cron = croniter(cron, now)
    cron.get_next(datetime.datetime)
    next_time = cron.get_next(datetime.datetime)
    return (next_time - now).total_seconds()


def make_archive(path: Path, last_backup_time: int):
    if path.is_dir():
        root = path
        files_iter = path.rglob("*")
    else:
        root = path.parent
        files_iter = [path]

    files = []
    for filepath in files_iter:
        last_modification_time = int(os.path.getmtime(filepath))

        if last_modification_time >= last_backup_time:
            files.append(filepath)

    if not files:
        return datetime.datetime.now().timestamp(), None, True

    archive_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{path.name}.zip"
    archive_dir = Path.home() / ".backuper"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / archive_name
    os.chdir(archive_dir)

    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for full_path in files:
            relative_path = os.path.relpath(full_path, root)
            zf.write(full_path, relative_path)

    return datetime.datetime.now().timestamp(), archive_path, False
