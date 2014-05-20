from tablesplitter.command.base import BaseCommand
from tablesplitter.web import app

class Command(BaseCommand):
    name = 'runserver'

    help = "Run the web interface for this app using a local development server"

    def run(self, args):
        app.run(debug=True)
