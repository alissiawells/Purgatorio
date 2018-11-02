#!/usr/bin/env python3
import os
import sys
from threading import Thread
import daemonize
from time import sleep
import filecmp
import shutil
import json
import hashlib
from flask import Flask, request, send_from_directory, jsonify, Response
from werkzeug.utils import secure_filename


class Daemon:

    def __init__(self):
        pass

    def main(self):

        UPLOAD_FOLDER = os.path.abspath('store')
        TRASH = os.path.abspath('removed')
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

        for folder in (UPLOAD_FOLDER, TRASH):
            if not os.path.exists(folder):
                os.makedirs(folder)

        app = Flask(__name__)
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        app.config['TRASH'] = TRASH

        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

        def encrypt(filename):
            with open(filename, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()

        def __CheckIdenticalFile(file_hash, directory):
            files = os.listdir(directory)
            isIdentical = False
            if files and os.path.exists(directory):
                for f in files:
                    isIdentical |= filecmp.cmp(file_hash, os.path.join(directory, f))
                    if isIdentical:
                        return file_hash, f
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
                    file_hash = encrypt(filename)
                    file.save(os.path.join(app.config['TMP_DIR'], file_hash))
                    file_dir = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[:2])
                    file_path = file_dir + "/" + file_hash
                    checkIdentical = __CheckIdenticalFile(os.path.join(app.config['TMP_DIR'], file_hash, file_dir))
                    if not checkIdentical:
                        shutil.copyfile(os.path.join(app.config['TMP_DIR'], file_hash), os.path.join(app.config['UPLOAD_FOLDER'], file_hash[:2], file_hash))
                        app.logger.info("Removing tmp file from tmp filesystem")
                        os.remove(os.path.join(app.config['TMP_DIR'], file_hash))
                        message = {'message': 'Uploaded', "http-response": "%s%" % file_hash}
                        response = Response(json.dumps(message), status=200, mimetype='application/json')
                        return response
                    app.logger.info("removing tmp file %s" % file_hash)
                    os.remove(os.path.join(app.config['TMP_DIR'], file_hash))
                    error_mess = {'message': 'File %s has already been uploaded' % file_hash}
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

        @app.route('/store/<string:file_hash>', methods=['GET'])
        def uploaded_file(file_hash):
            # This function displays content of the uploaded file
            return send_from_directory(app.config['UPLOAD_FOLDER'],
                                       file_hash)


        @app.route('/store/<string:file_hash>', methods=['DELETE'])
        def delete_item(file_hash):
            file_path = os.path.join(UPLOAD_FOLDER, file_hash[:2], file_hash)
            if os.path.exists(file_path):
                shutil.move(file_hash, os.path.join(app.config['TRASH'], file_hash))
                os.remove(file_path)
                app.logger.info("File %s removed" % file_hash)
                removeMsg = {"message": "File %s is moved to trash" %(file_hash)}
                response = Response(json.dumps(removeMsg), status=202, mimetype='application/json')
                return response
            else:
                NoFileError = {
                "error": "The file %s was not found" % file_hash
                }
                app.logger.info("File %s was not found" % file_hash)
                response = Response(json.dumps(NoFileError), status=404, mimetype='application/json')
                return response


        @app.errorhandler(400)
        def Bad_Request(error):
            return 'Where is the file?', 400


        @app.errorhandler(409)
        def Bad_Request(error):
            response = jsonify(error.description['message'])
            return response

        Thread(target=app.run).start()
        self.loop()

    def loop(self):
        i = 0
        while True:
            self.data.append(i)
            i += 1
            sleep(1)


if __name__ == "__main__":

    def start():
        daemonize.Daemonize(app="daemon", pid="/tmp/daemon.pid", action=Daemon().main).start()


    def stop():
        if not os.path.exists("/tmp/daemon.pid"):
            sys.exit(0)
        with open("/tmp/daemon.pid", "r") as pidfile:
            pid = pidfile.read()
        os.system('kill -9 %s' % pid)


    def foreground():
        Daemon().main()

    try:
        if sys.argv[1] == "start":
            start()
        elif sys.argv[1] == "stop":
            stop()
        elif sys.argv[1] == "restart":
            stop()
            start()
        elif sys.argv[1] == "foreground":
            foreground()
    except IndexError as e:
        print("usage: start|stop|restart|foreground")
        sys.exit(1)