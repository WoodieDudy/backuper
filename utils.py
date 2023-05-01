import json
import os
import zipfile
import datetime

from croniter import croniter

processes_info_file = 'processes.json'


def get_running_processes() -> dict:
    try:
        with open(processes_info_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data


def save_processes_info(data: dict):
    with open(processes_info_file, 'w') as f:
        json.dump(data, f)


def cron_parser(cron):
    now = datetime.datetime.now()
    cron = croniter(cron, now)
    cron.get_next(datetime.datetime)
    next_time = cron.get_next(datetime.datetime)
    return (next_time - now).total_seconds()


def zip_directory(path, output_zipfile):
    if os.path.isfile(path):
        root_dir = os.path.dirname(path)
    else:
        root_dir = path

    with zipfile.ZipFile(output_zipfile, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, root_dir)
                zipf.write(full_path, relative_path)
