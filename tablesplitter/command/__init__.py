from tablesplitter.command import (initdb, create_project, split_pdf, 
    detect_cells, split_img, ocr_img, merge, runserver)

class CommandRegistry(dict):
    def register(self, cls):
        self[cls.name] = cls

registry = CommandRegistry()

registry.register(initdb.Command)
registry.register(create_project.Command)
registry.register(split_pdf.Command)
registry.register(detect_cells.Command)
registry.register(split_img.Command)
registry.register(ocr_img.Command)
registry.register(merge.Command)
registry.register(runserver.Command)
