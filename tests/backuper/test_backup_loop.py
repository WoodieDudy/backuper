import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from backuper.disks.base_disk import BaseDisk
from backuper.backup_loop import start_process
from backuper.controller import FiniteController
from backuper.archive_maker import ArchiveMaker


class FakeProcessesRepository:
    def __init__(self):
        self.processes = {}

    def add_process(self, name, info):
        self.processes[name] = info

    def stop_process(self, name):
        pass

    def __contains__(self, item):
        return item in self.processes


@pytest.fixture
def disk_mock():
    return Mock(spec=BaseDisk)


@pytest.fixture
def controller():
    return FiniteController(1)


@pytest.fixture
def processes_repository():
    return FakeProcessesRepository()


@pytest.fixture
def mock_cron_parser():
    with patch('backuper.backup_loop.cron_parser') as mock:
        yield mock


@pytest.fixture
def mock_stop_process():
    with patch.object(FakeProcessesRepository, 'stop_process') as mock:
        yield mock


@pytest.fixture
def mock_make_fresh_archive():
    with patch.object(ArchiveMaker, 'make_fresh_archive') as mock:
        yield mock


def test_start_process_with_existing_name(disk_mock, controller, processes_repository, mock_stop_process, mock_cron_parser):
    processes_repository.add_process('test', {})
    mock_cron_parser.return_value = 0.1

    start_process('test', Path('/path/to/folder'), '0 * * * *', disk_mock, controller, processes_repository)

    mock_stop_process.assert_called_once()


def test_start_process_with_new_name(disk_mock, controller, processes_repository, mock_stop_process, mock_cron_parser):
    mock_cron_parser.return_value = 0.1

    start_process('new_test', Path('/path/to/folder'), '0 * * * *', disk_mock, controller, processes_repository)

    mock_stop_process.assert_not_called()


def test_start_process_no_files_to_archive(disk_mock, controller, processes_repository, mock_make_fresh_archive, mock_cron_parser):
    mock_make_fresh_archive.return_value = None
    mock_cron_parser.return_value = 0.1

    start_process('new_test', Path('/path/to/folder'), '0 * * * *', disk_mock, controller, processes_repository)

    disk_mock.upload.assert_not_called()


def test_start_process_with_files_to_archive(disk_mock, controller, processes_repository, mock_make_fresh_archive, mock_cron_parser):
    processes_repository.add_process('new_test', {})
    mock_make_fresh_archive.return_value = '/path/to/archive.zip'
    mock_cron_parser.return_value = 0.1

    start_process('new_test', Path('/path/to/folder'), '0 * * * *', disk_mock, controller, processes_repository)

    disk_mock.upload.assert_called_once()
