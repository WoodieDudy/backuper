from disks.base_disk import BaseDisk
from disks.google_disk import GoogleDisk
from disks.yandex_disk import YandexDisk


def get_disk(name: str) -> BaseDisk:
    """
    Возвращает диск по имени

    :param name: имя хранилища
    :return: объект соответствующего класса
    """
    if name == "yandex":
        return YandexDisk()
    elif name == "google":
        return GoogleDisk()
    else:
        raise ValueError("Invalid disk name")
