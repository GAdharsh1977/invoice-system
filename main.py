from core.parserDispatcher import ParserDispatcher
from parsers.xml_parser import XMLParser
from parsers.cii_parser import CIIParser
from parsers.ubl_parser import UBLParser
from parsers.pdf_parser import PDFParser

from core.mapperDispatcher import MapperDispatcher
from mapper.ocr import ImageMapper
from mapper.cii import CIIMapper
from mapper.xml import XMLMapper
from mapper.ubl import UBLMapper
from mapper.pdf import PDFMapper
from parsers.ocr import OCRParser

dispatcher = ParserDispatcher()

dispatcher.register(XMLParser())
dispatcher.register(CIIParser())
dispatcher.register(UBLParser())
dispatcher.register(PDFParser())
dispatcher.register(OCRParser())

mapper_dispatcher = MapperDispatcher()

mapper_dispatcher.register(UBLMapper())
mapper_dispatcher.register(CIIMapper())
mapper_dispatcher.register(PDFMapper())
mapper_dispatcher.register(ImageMapper())
mapper_dispatcher.register(XMLMapper())

