from pathlib import Path

root_save = Path.home() / ".backuper"

processes_info_file = root_save / "processes.json"
secrets_file = root_save / "secrets.json"
archives_dir = root_save / "archives"
logs_file = root_save / "logs.txt"
google_secrets_file = root_save / "google_secrets.json"
google_credentials = root_save / "mycreds.json"
