from flask import (Flask, send_from_directory)

from tablesplitter.conf import settings
from tablesplitter.api import CellResource, TextResource

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object(settings)

app.config.from_envvar('TABLESPLITTER_SETTINGS_MODULE', silent=True)

@app.route('/img/cell/<path:filename>')
def cell_image(filename):
    return send_from_directory(app.config['SPLIT_DIR'],
        filename)

CellResource.add_url_rules(app, rule_prefix='/api/cells/')
TextResource.add_url_rules(app, rule_prefix='/api/text/')
