import os
import sys

import yadisk

from disks.base_disk import BaseDisk


class YandexDisk(BaseDisk):
    def __init__(self):
        self.disk = yadisk.YaDisk('secret', 'secret')

    def try_auth(self) -> bool:
        url = self.disk.get_code_url()
        print("Go to the following url: %s" % url)
        code = input("Enter the confirmation code: ")

        try:
            response = self.disk.get_token(code)
        except yadisk.exceptions.BadRequestError:
            print("Bad code")
            sys.exit(1)

        self.disk.token = response.access_token
        return self.disk.check_token()

    def upload(self, file_to_upload_path) -> None:
        with open(file_to_upload_path, "rb") as f:
            print("Uploading")
            self.disk.upload(f, f'/{os.path.basename(file_to_upload_path)}', overwrite=True, timeout=250)
            print("Upload finished")

    def list_of_files(self) -> list[str]:
        return list(map(lambda x: x.toString, list(self.disk.listdir('/'))))

    def download(self) -> None:
        pass


if __name__ == '__main__':
    yandex_disk = YandexDisk()
    yandex_disk.try_auth()
    yandex_disk.upload(r"C:/Users/marga/.backuper/2023-05-01_13-15-44_apache-maven-3.8.6.zip")
