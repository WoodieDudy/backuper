import os

import yadisk
from yadisk.exceptions import PathNotFoundError, BadRequestError

from .base_disk import BaseDisk
from ..utils import extract_secrets_from_json


class YandexDisk(BaseDisk):  # pragma: no cover
    """
    Класс для работы с яндекс диском
    """

    def __init__(self):
        self.disk = None
        secrets = extract_secrets_from_json(self.__class__.__name__)
        if not secrets:
            self.disk_authentication()
            secrets = extract_secrets_from_json(self.__class__.__name__)

        app_id, app_secret = secrets["app_info"]["app_id"], secrets["app_info"]["app_secret"]
        self.disk = yadisk.YaDisk(app_id, app_secret)
        self.disk.token = secrets["token"]
        self.root_path = "/"

    def _auth_app(self):
        app_id = input("Enter app id: ")
        app_secret = input("Enter app secret: ")
        return {"app_info": {"app_id": app_id, "app_secret": app_secret}}

    def _auth_user(self):
        app_info = extract_secrets_from_json(self.__class__.__name__)["app_info"]
        self.disk = yadisk.YaDisk(app_info["app_id"], app_info["app_secret"])
        url = self.disk.get_code_url()
        print(f"Go to the following url: {url}")
        code = input("Enter the confirmation code: ")

        try:
            response = self.disk.get_token(code)
            token = response.access_token
            self.disk.token = token
        except BadRequestError:
            raise ValueError("Bad code")

        return {"token": token}

    def upload(self, file_to_upload_path) -> None:
        with open(file_to_upload_path, "rb") as f:
            self.disk.upload(f, f"/{os.path.basename(file_to_upload_path)}", overwrite=True, timeout=250)

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
