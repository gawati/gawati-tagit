from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
import os
from werkzeug.utils import secure_filename
from tagger import tag_doc

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['UPLOAD_FOLDER'] = 'tmp/'

ALLOWED_EXTENSIONS = set(['txt', 'xml'])

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/tag', methods=['POST', 'GET'])
def get_tags():
  if 'file' not in request.files:
    return render_template('index.html', error="No file part")

  file = request.files['file']
  if file.filename == '':
    return render_template('index.html', error="No Selected File")

  if allowed_file(file.filename):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    tags = tag_doc(filepath)
    return render_template('index.html', tags=tags)
  else:
    return render_template('index.html', error="File type not allowed")

  return render_template('index.html')