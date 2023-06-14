import pytest

from backuper.disk_utils import get_disk, YandexDisk, GoogleDisk


def test_get_disk_yandex():
    disk = get_disk("yandex")
    assert disk == YandexDisk


def test_get_disk_google():
    disk = get_disk("google")
    assert disk == GoogleDisk


def test_get_disk_invalid():
    try:
        get_disk("invalid")
    except ValueError as e:
        assert str(e) == "Invalid disk name"
    else:
        pytest.fail("Expected ValueError was not raised")
