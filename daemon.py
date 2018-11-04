#!/usr/bin/env python3
import os
import sys
from threading import Thread
import daemonize
from time import sleep
import shutil
import json
import hashlib
from flask import Flask, request, send_from_directory, jsonify, Response
from werkzeug.utils import secure_filename


class Daemon:

    def main(self):

        UPLOAD_FOLDER = os.path.abspath('store')
        UPLOAD_FOLDER_TMP = os.path.abspath('tmp_store')
        TRASH = os.path.abspath('removed')
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

        for folder in (UPLOAD_FOLDER, UPLOAD_FOLDER_TMP, TRASH):
            if not os.path.exists(folder):
                os.makedirs(folder)

        app = Flask(__name__)
        app.debug = False
        app.use_reloader = False
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        app.config['UPLOAD_FOLDER_TMP'] = UPLOAD_FOLDER_TMP
        app.config['TRASH'] = TRASH

        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

        def encrypt(file):
            with open(file, 'rb') as f:
                return hashlib.sha512(f.read()).hexdigest()
        """
        It is recommended to use SHA-2 hashing:
        hashlib.sha224(f.read()).hexdigest()
        hashlib.sha512(f.read()).hexdigest() 

        But if you are not paranoid, you can use MD5 or SHA-1:
        hashlib.md5(f.read()).hexdigest()
        hashlib.sha1(f.read()).hexdigest()

        Although meaningful files will not be clobbered, contrived files can be generated.
        """

        @app.route('/', methods=['GET', 'POST'])
        def upload_file():

        # save to temporary directory because Flask doesn't save data from files > 500kb in request.files['file']
            if request.method == 'POST':
                file = request.files['file']
                filename = secure_filename(file.filename)
                if file and allowed_file(filename):
                    tmp_path = os.path.join(app.config['UPLOAD_FOLDER_TMP'], filename)
                    file.save(tmp_path) 
                    file.close()

         # move from tmp dir to storage if the file is identical
                    file_hash = encrypt(tmp_path)
                    file_dir = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[:2])
                    os.makedirs(file_dir, exist_ok=True)
                    file_path = os.path.join(file_dir, file_hash)
                    if not os.path.exists(file_path):
                        shutil.copyfile(tmp_path, file_path)
                        message = {'http-response': file_hash}
                        response = Response(json.dumps(message), status=200, mimetype='application/json')
                        return response
                    else:
                        error_mess = {'message': 'File %s has already been uploaded' % file_hash}
                        response = Response(json.dumps(error_mess), status=409, mimetype='application/json')
                        return response
                    app.logger.info("Removing tmp file from tmp filesystem")
                    os.remove(tmp_path)
        # invalid extensions
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


        @app.route('/store/<file_hash>', methods=['GET'])
        def download_file(file_hash):
            # get content of the uploaded file
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], file_hash[:2]),
                                       file_hash)


        @app.route('/store/<file_hash>', methods=['DELETE'])
        def delete_item(file_hash):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[:2], file_hash)
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

        @app.errorhandler(500)
        def Bad_Request(error):
            return 'Too deviant', 500

        Thread(target=app.run).start()
        self.loop()


    def loop(self):
        i = 0
        while True:
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
