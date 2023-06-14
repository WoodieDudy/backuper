import json
import os
import signal
from typing import Optional


class ProcessesRepository:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> dict[str, dict]:
        """
        Загружает информацию о процессах из файла.
        """
        try:
            with open(self.filepath) as f:
                data = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = {}
        return data

    def save(self, data: dict[str, dict]):
        """
        Сохраняет информацию о процессах в файл.
        """
        with open(self.filepath, 'w') as f:
            json.dump(data, f)

    def get_process(self, name: str) -> Optional[dict]:
        """
        Возвращает информацию о процессе по его имени.
        """
        processes = self.load()
        return processes.get(name)

    def add_process(self, name: str, info: dict):
        """
        Добавляет новый процесс в репозиторий.
        """
        processes = self.load()
        processes[name] = info
        self.save(processes)

    def remove_process(self, name: str):
        """
        Удаляет процесс из репозитория.
        """
        processes = self.load()
        if name in processes:
            del processes[name]
            self.save(processes)

    def stop_process(self, name: str) -> bool:
        """
        Останавливает процесс по его имени.
        """
        process_info = self.get_process(name)
        if process_info:
            try:
                os.kill(process_info["pid"], signal.SIGTERM)
                self.remove_process(name)
                return True
            except ProcessLookupError:
                return False
        return False

    def __contains__(self, item):
        return item in self.load()
