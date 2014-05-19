from tablesplitter.command.base import BaseCommand
from tablesplitter import models

class Command(BaseCommand):
    name = 'initdb'

    help = "Initialize database tables"
 
    def run(self, args):
        for attr_name in dir(models):
            if attr_name == "BaseModel":
                continue

            attr_val = getattr(models, attr_name)
            try:
                if issubclass(attr_val, models.BaseModel):
                    attr_val.create_table()
                    self.output("Created table for {}".format(attr_name))

            except TypeError:
                pass
