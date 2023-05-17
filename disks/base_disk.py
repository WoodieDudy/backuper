import abc


class BaseDisk(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def try_auth(self) -> bool: ...

    @abc.abstractmethod
    def upload(self, file_path: str) -> None: ...

    @abc.abstractmethod
    def list_of_files(self) -> list[str]: ...

    @abc.abstractmethod
    def download(self) -> None: ...

    @abc.abstractmethod
    def load_secrets(self) -> None: \
        """
        Присваивает значение секретов (токенов и т. д.) диску
        """

    @abc.abstractmethod
    def check_auth(self) -> bool: ...
