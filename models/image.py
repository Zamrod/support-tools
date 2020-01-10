import os


class Image:
    def __init__(self):
        self.tag = None
        self.name = None
        self.slug = None
        self.source_path = None

    def filename(self):
        if self.source_path is not None:
            return os.path.basename(self.source_path)
        else:
            return ""
