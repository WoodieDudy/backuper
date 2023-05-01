import datetime


class Logger:
    def __init__(self, file_name):
        self.file_name = file_name

    def log(self, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.file_name, 'a') as log_file:
            log_file.write(f'{timestamp} - {message}\n')
