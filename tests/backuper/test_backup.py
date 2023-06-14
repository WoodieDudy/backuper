from unittest.mock import patch, call

from backuper.backup import start_backup, stop_backup, get_backups


@patch('backuper.backup.is_disk_authed', return_value=False)
@patch('backuper.disk_utils.get_disk')
@patch('backuper.backup.print')
def test_start_backup_not_authed(mock_print, mock_get_disk, mock_is_disk_authed):
    mock_get_disk.return_value = lambda: None
    start_backup('yandex', 'cron', 'name', 'path')
    assert mock_print.call_args_list == [call("You're not authorized in disk"),
                                         call("Please, run 'python backup.py auth -d <disk>")]


@patch('backuper.processes_repository.ProcessesRepository')
@patch('backuper.backup.print')
@patch("json.load", return_value={"test": {"cron": "* * * * *", "pid": 90660}})
def test_get_backups_no_processes(mock_json_load, mock_print, mock_ProcessesRepository):
    get_backups()
    assert mock_print.call_args_list == [call("test"),
                                         call("\tcron: * * * * *"), call("\tpid: 90660")]
