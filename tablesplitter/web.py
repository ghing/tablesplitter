import csv
import os.path

from six import StringIO
from six.moves.urllib.parse import urlparse, urljoin

from flask import (Flask, abort, render_template, send_from_directory, request,
                   flash, redirect, url_for, Response)

from tablesplitter.api import CellResource, TextResource, ProjectResource
from tablesplitter.conf import settings
from tablesplitter.models import ImageFile, Project, SourceFile, SplitFile, Text

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object(settings)

app.config.from_envvar('TABLESPLITTER_SETTINGS_MODULE', silent=True)

app.secret_key = app.config['SECRET_KEY']

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.values.get('next')
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target) 

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
    project = source_file.project
    breadcrumbs = [
        (project.name, url_for('project', slug=project.slug)),
        (source_file.filename, None),
    ]
    return render_template('source_file.html', source_file=source_file,
        breadcrumbs=breadcrumbs)

@app.route('/image-files/<id>')
def image_file(id):
    image_file = ImageFile.get(ImageFile.id == id)
    project = image_file.source.project
    breadcrumbs = [
        (project.name, url_for('project', slug=project.slug)),
        (image_file.source.filename,
         url_for('source_file', id=image_file.source.id)),
        (image_file.filename, None),
    ]
    return render_template('image_file.html', image_file=image_file,
        breadcrumbs=breadcrumbs)

@app.route('/image-files/<id>/csv')
def image_csv(id):
    image_file = ImageFile.get(ImageFile.id == id)
    csvfile = StringIO()
    writer = csv.writer(csvfile)

    def generate():
        for row in image_file.get_data():
            writer.writerow(row)
            csvfile.seek(0)
            data = csvfile.read()
            csvfile.seek(0)
            csvfile.truncate()
            yield data

    base, ext = os.path.splitext(image_file.filename)
    csv_filename = "{}{}".format(base, ".csv") 
    resp = Response(generate(), mimetype='text/csv')
    resp.headers["Content-Disposition"] = "attachment; filename={}".format(csv_filename)
   
    return resp


@app.route('/cells/<id>')
def cell(id):
    cell = SplitFile.get(SplitFile.id == id)
    source_file = cell.source.source
    project = source_file.project
    label = "Row {}, Column {}".format(cell.row, cell.column)
    next_view = get_redirect_target()
    breadcrumbs = [
        (project.name, url_for('project', slug=project.slug)),
        (source_file.filename,
         url_for('source_file', id=source_file.id)),
        (cell.source.filename, url_for('image_file', id=cell.source.id)),
        (label, None),
    ]
    return render_template('cell.html', cell=cell, breadcrumbs=breadcrumbs,
        next=next_view)

@app.route('/cells/<id>/add-text', methods=['POST'])
def add_cell_text(id):
    cell = SplitFile.get(SplitFile.id == id)
    text = request.form['text']
    Text.create(source=cell, method='manual',
            text=text, user_id=request.form['user_id'])
    flash("Text version '{}' added.".format(text), 'success')

    return redirect_back(url_for('cell', id=id))

@app.route('/text/<id>/accept')
def accept_text(id):
    text = Text.get(Text.id == id)
    try:
        accepted = request.values['accepted'].lower() == "true"
    except KeyError:
        accepted = False

    text.accepted = accepted
    text.save()

    return redirect_back(url_for('cell', id=text.source.id))


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
ProjectResource.add_url_rules(app, rule_prefix='/api/projects/')
