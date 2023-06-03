import abc
import re


class BaseDisk(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def try_auth(self) -> bool: \
        """
        Делает попытку авторизоваться и сохранить токен авторизации в JSON

        :return: результат проверки успешности авторизации
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

    @abc.abstractmethod
    def load_secrets(self) -> None: \
        """
        Присваивает значение секретов (токенов и т. д.) диску
        """

    @abc.abstractmethod
    def check_auth(self) -> bool: \
        """
        Проверяет, авторизован ли пользователь
        :return: True, если да; False, если нет
        """


    @staticmethod
    def filter_files(files: list) -> list:
        """
        Выделяет среди файлов на диске только бэкапы
        :param files: список всех файлов в корневой директории диска
        :return: отфильтрованный список файлов
        """
        return list(filter(lambda x: re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_.*.zip", x), files))
