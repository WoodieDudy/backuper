import json
import os

import requests
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from backuper.utils import extract_secrets_from_json
from .base_disk import BaseDisk
from backuper.defs import google_secrets_file, google_credentials


class GoogleDisk(BaseDisk): # pragma: no cover
    """
    Класс для работы с Google Drive
    """

    def __init__(self):
        self.gauth = GoogleAuth()
        secrets = extract_secrets_from_json(self.__class__.__name__)
        if not secrets:
            self.disk_authentication()

        self.gauth.LoadCredentialsFile(google_credentials)
        self.drive = GoogleDrive(self.gauth)
        self.root_path = 'root'

    def _auth_app(self):
        client_id = input("input client id: ")
        client_secret = input("input client secret: ")

        if not self._secrets_are_valid(client_id, client_secret):
            raise ValueError("Неверные секреты приложния")

        with open(google_secrets_file, "w") as f:
            json.dump(self._get_auth_json(client_id, client_secret), f)

        self.gauth.LoadClientConfigFile(google_secrets_file)
        os.remove(google_secrets_file)

        return {"client_id": client_id, "client_secret": client_secret}

    def _auth_user(self):
        if self.gauth.credentials is None:
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            self.gauth.Refresh()
        else:
            self.gauth.Authorize()

        self.gauth.SaveCredentialsFile(google_credentials)

    def upload(self, file_to_upload_path) -> None:
        file_drive = self.drive.CreateFile({'title': os.path.basename(file_to_upload_path)})
        file_drive.SetContentFile(file_to_upload_path)
        file_drive.Upload()
        print("Upload finished")

    def list_of_files(self) -> list[str]:
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        names = [file['title'] for file in file_list]
        return self.filter_files(names)

    def download(self, filename: str) -> None:
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file['title'] == filename:
                file.GetContentFile(filename)
                break
        else:
            raise ValueError("No such file on disk")

    @staticmethod
    def _get_auth_json(client_id, client_secret):
        return {"installed": {"client_id": client_id,
                              "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                              "token_uri": "https://oauth2.googleapis.com/token",
                              "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                              "client_secret": client_secret,
                              "redirect_uris": ["http://localhost"]}}

    @staticmethod
    def _secrets_are_valid(client_id, client_secret):
        url = "https://www.googleapis.com/oauth2/v4/token"

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": "dummy",
            "grant_type": "refresh_token",
        }

        response = requests.post(url, data=payload)

        if response.status_code == 400:
            json_response = response.json()
            return json_response["error"] == "invalid_grant" and json_response["error_description"] == "Bad Request"
        return False
