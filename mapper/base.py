from abc import ABC, abstractmethod
from utils.schema import Invoice

class BaseMapper(ABC):
    format_name: str

    @abstractmethod
    def map(self, parsed: dict) -> Invoice:
        pass
    