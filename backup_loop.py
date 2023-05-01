import os
import signal
import sys
import subprocess
import json

from backuper import _parse_args


processes_info_file = 'processes.json'


def start_process():
    args = _parse_args()
    try:
        with open(processes_info_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    if args.path in data:
        data[args.path]['cron'] = args.rate
        os.kill(data[args.path]['pid'], signal.SIGTERM)

    run(args)

    data[args.path]['pid'] = os.getpid()
    data[args.path]['cron'] = args.rate

    with open(processes_info_file, 'w') as f:
        json.dump(data, f)

    print(f"Background process started with PID {os.getpid()}")


def stop_process():
    try:
        with open(processes_info_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No processes running")
        return

    with open(pid_file, 'r') as f:
        pid = int(f.read())

    try:
        os.kill(pid, signal.SIGTERM)
        os.remove(pid_file)
        print(f"Background process with PID {pid} stopped.")
    except OSError:
        print(f"Error: Unable to stop process with PID {pid}")


def main():
    args = _parse_args()
