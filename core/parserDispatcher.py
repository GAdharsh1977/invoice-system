from parsers.parser import BaseParser

class ParserDispatcher:
    def __init__(self):
        self.parsers = []

    def register(self, parser: BaseParser):
        self.parsers.append(parser)

    def get_parser(self, format_hint: str):
        for p in self.parsers:
            if p.format_name == format_hint:
                return p
        raise Exception(f"No Parser Found for {format_hint}")
    
    def get(self, format_hint: str):
        return self.get_parser(format_hint)
    
    def parse(self, file_path, format_hint):
        parser = self.get_parser(format_hint)
        return parser.parse(file_path)