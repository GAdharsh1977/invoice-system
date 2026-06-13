from abc import ABC, abstractmethod

class BaseParser(ABC):
    format_name: str 
    @abstractmethod
    def parse(self, file_path: str) -> dict:
        pass