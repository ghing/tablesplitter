from flask import (Flask, abort, render_template, send_from_directory)

from tablesplitter.api import CellResource, TextResource
from tablesplitter.conf import settings
from tablesplitter.models import ImageFile, Project, SourceFile

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object(settings)

app.config.from_envvar('TABLESPLITTER_SETTINGS_MODULE', silent=True)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    projects = Project.select() 
    return render_template('projects.html', projects=projects)

@app.route('/projects/<slug>')
def project(slug):
    project = Project.get(Project.slug == slug)
    return render_template('project.html', project=project)

@app.route('/source-files/<id>')
def source_file(id):
    source_file = SourceFile.get(SourceFile.id == id)
    return render_template('source_file.html', source_file=source_file)

@app.route('/image-files/<id>')
def image_file(id):
    image_file = ImageFile.get(ImageFile.id == id)
    return render_template('image_file.html', image_file=image_file)

@app.route('/img/<image_type>/<path:filename>')
def image(image_type, filename):
    if image_type == "cell":
        image_dir = app.config['SPLIT_DIR']
    elif image_type == "extracted":
        image_dir = app.config['IMG_DIR']
    else:
        abort(404)

    return send_from_directory(image_dir, filename)


CellResource.add_url_rules(app, rule_prefix='/api/cells/')
TextResource.add_url_rules(app, rule_prefix='/api/text/')
