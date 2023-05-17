import json
import os
import zipfile
import datetime

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
    with open(processes_info_file, 'w') as f:
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
