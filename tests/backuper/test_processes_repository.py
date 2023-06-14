import signal
from unittest import mock

from backuper.processes_repository import ProcessesRepository


def test_load():
    with mock.patch("builtins.open", mock.mock_open(read_data='{"proc1": {"pid": 12345, "path": "/path/to/proc1"}}')):
        repo = ProcessesRepository("/path/to/repo")
        data = repo.load()
        assert data == {"proc1": {"pid": 12345, "path": "/path/to/proc1"}}


def test_save():
    with mock.patch("builtins.open", mock.mock_open()) as mock_file, \
            mock.patch("json.dump") as mock_json_dump:
        repo = ProcessesRepository("/path/to/repo")
        repo.save({"proc1": {"pid": 12345, "path": "/path/to/proc1"}})
        mock_file.assert_called_once_with("/path/to/repo", "w")
        mock_json_dump.assert_called_once_with({"proc1": {"pid": 12345, "path": "/path/to/proc1"}}, mock_file())


def test_add_process():
    with mock.patch("builtins.open", mock.mock_open(read_data='{}')) as mock_file, \
            mock.patch("json.dump") as mock_json_dump:
        repo = ProcessesRepository("/path/to/repo")
        repo.add_process("proc1", {"pid": 12345, "path": "/path/to/proc1"})
        mock_json_dump.assert_called_once()


def test_remove_process():
    with mock.patch("builtins.open",
                    mock.mock_open(read_data='{"proc1": {"pid": 12345, "path": "/path/to/proc1"}}')) as mock_file, \
            mock.patch("json.dump") as mock_json_dump:
        repo = ProcessesRepository("/path/to/repo")
        repo.remove_process("proc1")
        mock_json_dump.assert_called_once()


def test_stop_process():
    with mock.patch("builtins.open",
                    mock.mock_open(read_data='{"proc1": {"pid": 12345, "path": "/path/to/proc1"}}')) as mock_file, \
            mock.patch("os.kill") as mock_os_kill, \
            mock.patch("json.dump") as mock_json_dump:
        repo = ProcessesRepository("/path/to/repo")
        result = repo.stop_process("proc1")
        mock_os_kill.assert_called_once_with(12345, signal.SIGTERM)
        assert result is True
        mock_json_dump.assert_called_once()


def test_contains():
    with mock.patch("builtins.open",
                    mock.mock_open(read_data='{"proc1": {"pid": 12345, "path": "/path/to/proc1"}}')) as mock_file:
        repo = ProcessesRepository("/path/to/repo")
        assert "proc1" in repo
        assert "proc2" not in repo
