from tablesplitter.command.base import BaseCommand
from tablesplitter.models import Project

class Command(BaseCommand):
    name = 'create_project'

    help = "Create a new project in the database"

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('name')

    def run(self, args):
        Project.create(name=args.name)
