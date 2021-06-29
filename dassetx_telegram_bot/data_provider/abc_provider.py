from abc import ABCMeta, abstractmethod
from typing import Any


class DataProviderABC(metaclass=ABCMeta):
    """Provider behaves like a key-value storage"""

    @abstractmethod
    def get(self, key: str) -> Any:
        """request access to key

        :param key: a key name in string
        :return: Any type of data
        """
