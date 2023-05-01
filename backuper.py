import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

from croniter import croniter

from utils import get_running_processes, save_processes_info


def _parse_args():
    def path(args_string):
        res_path = Path(args_string)
        if not res_path.exists():
            raise ValueError('This path doesn\'t exist')
        print(res_path)
        return res_path

    def cron(args_string):
        if not croniter.is_valid(args_string):
            raise ValueError("Invalid cron format")
        return args_string

    def disk(args_string):
        if args_string not in ['yandex', 'google']:
            raise ValueError('Possible choices: [yandex, google]')
        return args_string

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    start_parser = subparsers.add_parser('start')
    start_parser.set_defaults(cmd='start')
    start_parser.add_argument("-p", "--path", help="", type=path)
    start_parser.add_argument("-c", "--cron", help="backup rate", type=cron)
    start_parser.add_argument("-d", "--disk", help="[google, yandex]", type=disk)
    start_parser.add_argument("-n", "--name", help="name of process", type=str)

    stop_parser = subparsers.add_parser('stop')
    stop_parser.set_defaults(cmd='stop')
    stop_parser.add_argument("-n", "--name", help="name of process", type=str)

    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(cmd='list')

    args = parser.parse_args()
    return args


def main():
    args = _parse_args()

    if args.cmd == 'start':
        print("start")
        p = subprocess.Popen(
            [sys.executable, "backup_loop.py", "start", "-p", str(args.path), "-c", args.cron, "-d", args.disk, "-n", args.name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # TODO мб не создавать два раза
        )
        print(p.pid)

    elif args.cmd == 'stop':
        running_processes = get_running_processes()
        name = args.name
        if name not in running_processes:
            print(f"Error: Process {name} not found")
            return
        pid = running_processes[name]['pid']
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Background process with PID {pid} stopped.")
            del running_processes[name]
        except OSError:
            print(f"Error: Unable to stop process with PID {pid}")
        save_processes_info(running_processes)

    elif args.cmd == 'list':
        running_processes = get_running_processes()
        if not running_processes:
            print('No running processes')
            return

        for name, info in running_processes.items():
            print(name)
            for key, value in info.items():
                print(f'\t{key}: {value}')
    else:
        raise ValueError('Unknown command')


if __name__ == '__main__':
    main()
