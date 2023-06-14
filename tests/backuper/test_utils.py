import pytest
import os.path
from unittest.mock import patch, mock_open
import datetime
import os
import json

from backuper.utils import make_app_dirs, extract_secrets_from_json, save_secrets, cron_parser, filter_files_by_time


def test_make_app_dirs_already_exist(tmpdir):
    temp_dir = tmpdir.mkdir("test_dir_exist")

    root_save = os.path.join(temp_dir, "root_save")
    archives_dir = os.path.join(temp_dir, "archives_dir")

    os.makedirs(root_save, exist_ok=True)
    os.makedirs(archives_dir, exist_ok=True)

    make_app_dirs()

    assert os.path.isdir(root_save)
    assert os.path.isdir(archives_dir)


def test_make_app_dirs_not_exist(tmpdir):
    temp_dir = tmpdir.mkdir("test_dir_not_exist")

    root_save = temp_dir.mkdir("root_save")
    archives_dir = temp_dir.mkdir("archives_dir")

    make_app_dirs()

    assert os.path.isdir(root_save)
    assert os.path.isdir(archives_dir)


def test_extract_secrets_from_json_empty_file():
    with patch("builtins.open", mock_open(read_data='{}')) as mock_file, \
            patch("json.load") as mock_json_load, \
            patch("os.path.getmtime") as mock_getmtime:
        mock_json_load.side_effect = json.JSONDecodeError('Expecting property name', '', 0)
        mock_getmtime.return_value = datetime.datetime.now().timestamp()
        result = extract_secrets_from_json()
        assert result == {}


def test_extract_secrets_from_json_file_not_found():
    with patch("builtins.open", mock_open()) as mock_file, \
            patch("os.path.getmtime") as mock_getmtime:
        mock_getmtime.return_value = datetime.datetime.now().timestamp()
        mock_file.side_effect = FileNotFoundError
        result = extract_secrets_from_json()
        assert result == {}


def test_extract_secrets_from_json_data_exists():
    mock_data = {"disk": {"secret": "value"}}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))) as mock_file, \
            patch("os.path.getmtime") as mock_getmtime:
        mock_getmtime.return_value = datetime.datetime.now().timestamp()
        result = extract_secrets_from_json("disk")
        assert result == mock_data["disk"]


def test_extract_secrets_from_json_old_mtime():
    mock_data = {"disk": {"secret": "value"}}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))) as mock_file, \
            patch("os.path.getmtime") as mock_getmtime:
        mock_getmtime.return_value = (datetime.datetime.now() - datetime.timedelta(days=11)).timestamp()
        result = extract_secrets_from_json("disk")
        assert result == {}


def test_save_secrets_update_existing_disk(tmpdir):
    secrets_file = tmpdir.join("secrets.json")

    data = {
        "yandex": {
            "api_key": "yandex_api_key",
            "api_secret": "yandex_api_secret"
        },
        "google": {
            "api_key": "google_api_key",
            "api_secret": "google_api_secret"
        }
    }

    with open(str(secrets_file), 'w') as f:
        json.dump(data, f)

    disk = "yandex"
    new_secrets = {
        "api_key": "new_yandex_api_key",
        "api_secret": "new_yandex_api_secret"
    }

    save_secrets(disk, new_secrets)

    updated_data = extract_secrets_from_json()
    assert updated_data[disk] == new_secrets


def test_save_secrets_add_new_disk(tmpdir):
    secrets_file = tmpdir.join("secrets.json")

    data = {
        "yandex": {
            "api_key": "yandex_api_key",
            "api_secret": "yandex_api_secret"
        },
        "google": {
            "api_key": "google_api_key",
            "api_secret": "google_api_secret"
        }
    }

    with open(str(secrets_file), 'w') as f:
        json.dump(data, f)

    disk = "test_disk"
    new_secrets = {
        "access_key": "test_disk_access_key",
        "secret_key": "test_disk_secret_key"
    }

    save_secrets(disk, new_secrets)

    updated_data = extract_secrets_from_json()
    assert updated_data[disk] == new_secrets


def test_save_none_secrets(tmpdir):
    data = {
        "yandex": {
            "api_key": "yandex_api_key",
            "api_secret": "yandex_api_secret"
        },
        "google": {
            "api_key": "google_api_key",
            "api_secret": "google_api_secret"
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))) as mock_file, \
            patch('json.dump') as mock_json_dump:
        disk = "google"
        none_secrets = None

        save_secrets(disk, none_secrets)

        updated_data = extract_secrets_from_json()

        assert updated_data == data


def test_cron_parser_every_minute():
    assert cron_parser('* * * * *') == 60


def test_cron_parser_every_x_minutes():
    assert cron_parser('*/15 * * * *') == 15 * 60


def test_cron_parser_every_hour():
    assert cron_parser('0 * * * *') == 60 * 60


def test_cron_parser_every_x_hours():
    assert cron_parser('0 */3 * * *') == 3 * 60 * 60


def test_cron_parser_invalid_format():
    with pytest.raises(ValueError):
        cron_parser('invalid cron expression')


def test_filter_files_by_time():
    files = ["file1.txt", "file2.txt", "file3.txt"]

    last_backup_time = 1632730800

    def mock_getmtime(filepath):
        if filepath == "file1.txt":
            return 1632723600
        elif filepath == "file2.txt":
            return 1632730800
        elif filepath == "file3.txt":
            return 1632759600  

    with patch("os.path.getmtime", side_effect=mock_getmtime):
        result = filter_files_by_time(files, last_backup_time)

        expected_result = {"file2.txt", "file3.txt"}
        assert result == expected_result
