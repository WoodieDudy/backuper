from typing import Type

from .utils import extract_secrets_from_json
from .disks.base_disk import BaseDisk
from .disks.google_disk import GoogleDisk
from .disks.yandex_disk import YandexDisk


def get_disk(name: str) -> Type[BaseDisk]:
    """
    Возвращает класс, соответствующий имени диска

    :param name: имя хранилища
    :return: объект соответствующего класса
    """
    if name == "yandex":
        return YandexDisk
    if name == "google":
        return GoogleDisk
    else:
        raise ValueError("Invalid disk name")


def is_disk_authed(name: str) -> bool:
    """
    Проверяет, авторизован ли диск
    :return: True, если да; False, если нет
    """
    return bool(extract_secrets_from_json(name))
