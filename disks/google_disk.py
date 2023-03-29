import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.auth import AuthError

from .base_disk import BaseDisk


class GoogleDisk(BaseDisk):
    def __init__(self):
        self.drive = None

    def try_auth(self) -> bool:
        try:
            gauth = GoogleAuth()
            self.drive = GoogleDrive(gauth)
            return True
        except AuthError:
            return False

    def upload(self, file_path) -> None:
        gfile = self.drive.CreateFile({'title': os.path.basename(file_path)})
        gfile.SetContentFile(file_path)
        gfile.Upload()

    def list_of_files(self) -> list[str]:
        pass

    def download(self) -> None:
        pass


if __name__ == '__main__':
    google_disk = GoogleDisk()
    google_disk.try_auth()
    google_disk.upload('README.md')
