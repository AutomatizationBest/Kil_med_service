from flask import Flask, request, jsonify, send_file, url_for, send_from_directory
import os
import logging
from io import BytesIO
from flask_cors import CORS, cross_origin
from table_remake import transfer_data_kp_to_spec
import asyncio


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}}, methods=['POST', 'GET'])
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["POST","GET","PUT"])
@cross_origin(methods=["GET","POST","PUT"])
def upload_file():

    if request.method=="POST":
        file = request.files['file']

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        answer = transfer_data_kp_to_spec(kp_path=file_path, spec_path='spec.xlsx', output_path='answer.xlsx')
        
    return send_file(answer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',as_attachment=True)


@app.route("/kp",  methods=["POST","GET","PUT"])
@cross_origin(methods=["GET","POST","PUT"])
def list_users():
    if request.method=="POST":
        file = request.files['file']

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        answer=make_oleg_file(file_path)
    return send_file(answer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',as_attachment=True)


@app.route("/api/load_kp_file", methods=['POST'])
def load_kp_file():
    
    return {"answer" : "File load succesfully broooo!!!"}

if __name__ == "__main__":
    from parallel_oleg import make_oleg_file
    try:
        app.run(host="0.0.0.0", port=8000)
    except Exception as e:
        logging.error(f"Error occurred: {e}")