from flask import render_template, jsonify, request
import os
from tagit import app
from werkzeug.utils import secure_filename
from .tagger import tag_doc

app.config['UPLOAD_FOLDER'] = 'tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'xml'])

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/tag', methods=['POST'])
def tagit():
  if 'file' not in request.files:
    return render_template('index.html', error="No file part")

  file = request.files['file']
  if file.filename == '':
    return render_template('index.html', error="No Selected File")

  if allowed_file(file.filename):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    data = tag_doc(filepath)
    if 'error' in data:
      return render_template('index.html', error=data["error"])
    else:
      return render_template('index.html', tags=data["tags"])
  else:
    return render_template('index.html', error="File type not allowed")

  return render_template('index.html')

@app.route('/api/tag', methods=['POST'])
def tagit_api():
  print(len(request.files))
  if 'file' not in request.files:
    return jsonify(error="No file part"), 400

  file = request.files['file']
  if file.filename == '':
    return jsonify(error="No Selected File"), 400

  if allowed_file(file.filename):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    data = tag_doc(filepath)
    if 'error' in data:
      return jsonify(error=data["error"]), 500
    else:
      return jsonify(tags=data["tags"]), 200
  else:
    return jsonify(error="File type not allowed"), 400

  return jsonify(), 204

if __name__ == '__main__':
    app.run(debug=False, port=5001)