from pathlib import Path


root_save = Path.home() / ".backuper"

processes_info_file = root_save / "processes.json"
secrets_file = root_save / "secrets.json"
archives_dir = root_save / "archives"
