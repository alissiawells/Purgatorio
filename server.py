#!filer/bin/python
import os
import filecmp
import shutil
import json
import hashlib
from flask import Flask, request, send_from_directory, jsonify, Response
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.abspath('store')
TRASH = os.path.abspath('removed')

for folder in (UPLOAD_FOLDER, TRASH):
    if not os.path.exists(folder):
        os.makedirs(folder)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TRASH'] = TRASH
app.config['MAX_CONTENT_LENGTH'] = 6291456  # limit

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def encrypt(filename):
    with open(filename, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(6291456)  # limit
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def __CheckIdenticalFile(filehash, directory):
    files = os.listdir(directory)
    isIdentical = False
    if files and os.path.exists(directory):
        for f in files:
            isIdentical |= filecmp.cmp(filehash, os.path.join(directory, f))
            if isIdentical:
                return filehash, f
    return None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        temp_dir = "/tmp/tmp/"
        app.config['TMP_DIR'] = temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        file = request.files['file']
        filename = secure_filename(file.filename)
        if file and allowed_file(filename):
            filehash = encrypt(filename)
            file.save(os.path.join(app.config['TMP_DIR'], filehash))
            checkIdentical = __CheckIdenticalFile(os.path.join(app.config['TMP_DIR'], filehash),
                                                  app.config['UPLOAD_FOLDER'])
            if not checkIdentical:
                shutil.copyfile(os.path.join(app.config['TMP_DIR'], filehash), os.path.join(app.config['UPLOAD_FOLDER'], filehash))
                app.logger.info("Removing tmp file from tmp filesystem")
                os.remove(os.path.join(app.config['TMP_DIR'], filehash))
                message = {'message': 'File %s is uploaded' % filehash}
                response = Response(json.dumps(message), status=200, mimetype='application/json')
                return response
            app.logger.info("removing tmp file %s" % filehash)
            os.remove(os.path.join(app.config['TMP_DIR'], filehash))
            error_mess = {'message': 'File %s has already been uploaded' % filehash}
            response = Response(json.dumps(error_mess), status=409, mimetype='application/json')
        else:
            error_mess = {"error": "Only %s files are allowed to upload " %(list(ALLOWED_EXTENSIONS))}
            response = Response(json.dumps(error_mess), status=404, mimetype='application/json')
        return response
    return """
    <!doctype html>
    <title>Deviant storage</title>
    <h1>Upload your deviant file</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=upload>
    </form>
    """


@app.route('/store/<filehash>', methods=['GET'])
def uploaded_file(filehash):
    # This function displays content of the uploaded file
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filehash)


@app.route('/store/<filehash>', methods=['DELETE'])
def delete_item(filehash):
    filehash = os.path.join(UPLOAD_FOLDER, filehash)
    if os.path.exists(filehash):
        shutil.move(filehash, os.path.join(app.config['TRASH'], filehash))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filehash))
        app.logger.info("File %s removed" % filehash)
        removeMsg = {"message": "File %s moved to trash" %(filehash)}
        response = Response(json.dumps(removeMsg), status=202, mimetype='application/json')
        return response
    else:
        NoFileError = {
        "error": "The file %s was not found" % filehash
        }
        app.logger.info("File %s was not found" % filehash)
        response = Response(json.dumps(NoFileError), status=404, mimetype='application/json')
        return response


@app.errorhandler(413)
def request_entity_too_large(e):
    return 'File is too heavy', 413


@app.errorhandler(400)
def Bad_Request(error):
    return 'Where is the file?', 400


@app.errorhandler(409)
def Bad_Request(error):
    response = jsonify(error.description['message'])
    return response


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000, debug=True)
    except KeyboardInterrupt:  # fixes socket.error when another process is listening on the port after Ctrl+Z
        exit(0)
