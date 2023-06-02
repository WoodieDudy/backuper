import abc


class BaseDisk(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def try_auth(self) -> bool: \
        """
        Делает попытку авторизоваться и сохранить токен авторизации в JSON

        :return: результат проверки успешности авторизации
        """

    @abc.abstractmethod
    def upload(self, file_path: str) -> None: \
        """
        Открывает файл в байтовом представлении и загружает его на диск
        :param file_path: путь к файлу
        """

    @abc.abstractmethod
    def list_of_files(self) -> list[str]: \
        """
        Извлекает список файлов, находящихся на диске
        :return: список файлов
        """

    @abc.abstractmethod
    def download(self) -> None: \
        """
        Скачивает запрошенный файл с диска
        """

    @abc.abstractmethod
    def load_secrets(self) -> None: \
        """
        Присваивает значение секретов (токенов и т. д.) диску
        """

    @abc.abstractmethod
    def check_auth(self) -> bool: ...
