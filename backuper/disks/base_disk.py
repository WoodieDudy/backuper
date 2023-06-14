import abc
import re
from typing import Optional

from backuper.utils import extract_secrets_from_json, save_secrets


class BaseDisk: # pragma: no cover
    """
    Абстрактный диск
    """

    def disk_authentication(self) -> None:
        """
        Выполняет полностью или завершает процесс авторизации
        """

        disk_name = self.__class__.__name__
        secrets = extract_secrets_from_json(disk_name)
        if not secrets:
            secrets = self._auth_app()
            save_secrets(disk_name, secrets)

        auth_data = self._auth_user()

        save_secrets(disk_name, auth_data)

    @abc.abstractmethod
    def _auth_app(self) -> dict[str]: \
        """
        Проводит авторзацию приложения и возвращает словарь секретов
        :return: словарь секретов приложения
        """

    @abc.abstractmethod
    def _auth_user(self) -> Optional[dict[str]]: \
        """
        Проводит авторизацию пользователя в диске
        :return: None или секреты, если они есть
        """

    @abc.abstractmethod
    def upload(self, file_path: str) -> None: \
        """
        Открывает файл в байтовом представлении и загружает его на диск
        :param file_path: путь к файлу
        """

    @abc.abstractmethod
    def list_of_files(self) -> list[str]: \
        """
        Извлекает список файлов, находящихся на диске
        :return: список файлов
        """

    @abc.abstractmethod
    def download(self, filename: str) -> None: \
        """
        Скачивает запрошенный файл с диска
        """

    @staticmethod
    def filter_files(files: list) -> list:
        """
        Выделяет среди файлов на диске только бэкапы
        :param files: список всех файлов в корневой директории диска
        :return: отфильтрованный список файлов
        """
        return list(filter(lambda x: re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_.*.zip", x), files))


    def __repr__(self):
        return f"{self.__class__.__name__}()"