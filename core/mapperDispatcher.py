from mapper.ubl import UBLMapper
from mapper.cii import CIIMapper
from mapper.pdf import PDFMapper
from mapper.ocr import ImageMapper
from mapper.xml import XMLMapper


class MapperDispatcher:
    def __init__(self):
        self.mappers = {}

    def register(self, mapper):
        self.mappers[mapper.format_name] = mapper

    def get(self, format_name: str):
        mapper = self.mappers.get(format_name)
        if not mapper:
            raise Exception(f"No mapper for {format_name}")
        return mapper