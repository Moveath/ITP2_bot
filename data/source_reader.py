class SourceReader:
    def read(self, source_type: str, content: str) -> str:
        if source_type == "text":
            return content
        raise NotImplementedError("Басқа түрлер 3-адамға жүктелген.")