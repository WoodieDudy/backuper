import os
import sys

import yadisk
from yadisk.exceptions import PathNotFoundError, BadRequestError

from .base_disk import BaseDisk
from ..utils import extract_secrets_from_json, save_secrets


class YandexDisk(BaseDisk):
    """
    Класс для работы с яндекс диском
    """
    def __init__(self):
        app_id, app_secret = self.load_app_configuration()
        self.disk = yadisk.YaDisk(app_id, app_secret)

        self.root_path = "/"

    def load_app_configuration(self) -> tuple[str, str]:
        """
        Проверяет, авторизовано ли на устройстве приложение для работы с диском
        (есть ли файл конфигурации с id и секретом приложения).
        Если нет, запрашивает авторизацию.

        Далее извлекает информацию из файла конфигурации для инициализации диска.
        :return: кортеж из идентификатора приложения и его секрета
        """

        try:
            secrets = extract_secrets_from_json("yandex")
            app_info = secrets["app_info"]
        except KeyError:
            self.auth_app()
            app_info = extract_secrets_from_json("yandex")["app_info"]

        return app_info["app_id"], app_info["app_secret"]

    @staticmethod
    def auth_app():
        """
        Авторизация приложения для работы с яндекс диском
        """

        app_id = input("Enter app id: ")
        app_secret = input("Enter app secret: ")
        save_secrets("yandex", {"app_info": {"app_id": app_id, "app_secret": app_secret}})

    def try_auth(self) -> bool:
        url = self.disk.get_code_url()
        print("Go to the following url: %s" % url)
        code = input("Enter the confirmation code: ")

        try:
            response = self.disk.get_token(code)
        except BadRequestError:
            print("Bad code")
            sys.exit(1)

        self.disk.token = response.access_token
        return self.disk.check_token()

    def upload(self, file_to_upload_path) -> None:
        with open(file_to_upload_path, "rb") as f:
            print("Uploading")
            self.disk.upload(f, f"/{os.path.basename(file_to_upload_path)}", overwrite=True, timeout=250)
            print("Upload finished")

    def list_of_files(self) -> list[str]:
        files = list(self.disk.listdir("/"))
        names = [resource_obj['name'] for resource_obj in files]
        return self.filter_files(names)

    def download(self, filename: str) -> None:
        try:
            self.disk.download(f"{self.root_path}{filename}", filename)
        except PathNotFoundError:
            os.remove(filename)
            raise ValueError("No such file on disk")

    def check_auth(self) -> bool:
        return self.disk.check_token()

    def load_secrets(self):
        self.disk.token = extract_secrets_from_json("yandex")["access_token"]


if __name__ == '__main__':
    yandex_disk = YandexDisk()
    yandex_disk.try_auth()
    # yandex_disk.upload("README.md")
