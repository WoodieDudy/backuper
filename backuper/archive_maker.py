import os
import datetime

from backuper.utils import filter_files_by_time, make_archive


class ArchiveMaker:
    def __init__(self, path):
        self.path = path
        self.backuped_files = set()
        self.last_backup_time = 0

    def get_files_from_path(self):
        files_in_path = set()
        for root, dirs, files in os.walk(self.path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) > self.last_backup_time:
                    files_in_path.add(file_path)
        return files_in_path

    def make_fresh_archive(self):
        files_in_path = self.get_files_from_path()
        new_files = files_in_path - self.backuped_files
        updated_files = filter_files_by_time(files_in_path, self.last_backup_time)
        files_to_archive = updated_files | new_files

        if not files_to_archive:
            return None

        self.backuped_files |= files_to_archive
        archive_path = make_archive(self.path, files_to_archive)
        self.last_backup_time = datetime.datetime.now().timestamp()

        return archive_path
