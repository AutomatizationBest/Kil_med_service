# from flask import Flask, request
# import os
# import logging
# from flask_cors import CORS, cross_origin


# app = Flask(__name__)




# @app.route("/", methods=["POST","GET","PUT"])
# @cross_origin(methods=["GET","POST","PUT"])
# def base():
#     return request.data


# @app.route("/load_kp_file", methods=["POST","GET"])
# def load_kp_file():
#     return {"answer" : "File load succesfully broooo!!!"}

# CORS(app,origins=["http://localhost:3000"])
# cors = CORS(app, resources={r"/": {"origins": "*"}})
# cors=CORS(resources={
#     r"/*": {"origins":"*"}
#     })

# if __name__ == "__main__":
#     try:
#         app.run(port=8000)
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")


from flask import Flask, request, jsonify, send_file, url_for, send_from_directory
import os
import logging
from io import BytesIO
from flask_cors import CORS, cross_origin
from table_remake import transfer_data_kp_to_spec
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}}, methods=['POST', 'GET'])
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["POST","GET","PUT"])
@cross_origin(methods=["GET","POST","PUT"])
def upload_file():
    # if 'file' not in request.files:
    #     return jsonify({"error": "No file part in the request"}), 400
    # file=request.files['file']
    # file = request.f['file']
    if request.method=="POST":
        file = request.files['file']

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        answer = transfer_data_kp_to_spec(kp_path=file_path, spec_path='spec.xlsx', output_path='answer.xlsx')
        


        # file.save('../excel/src/media/')
        file_path_download='../uploads/'+file.filename
    return send_file(answer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',as_attachment=True)
    # send_file(file_path_downloa§d,as_attachment=True)
    # return jsonify({"message": "File uploaded successfully!", "file_path": file_path}), 200

    #    if 'file' not in request.files:
    #         return jsonify({"error": "No file part in the request"}), 400
    #     file = request.files['file']
        
    #     if file.filename == '':
    #         return jsonify({"error": "No file selected"}), 400
        
    #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    #     file.save(file_path)
        
    #     # Чтение файла и кодирование в base64
    #     with open(file_path, "rb") as f:
    #         encoded_file = base64.b64encode(f.read()).decode('utf-8')

    #     # Возвращаем закодированный файл
    #     return jsonify({"filename": file.filename, "file": encoded_file}), 200


@app.route("/api/v1/users")
def list_users():
    return "example bro, u got it"

# @app.route("/")
# def base():
#     file = request.files()
#     file.save
#     return {"answer" : "Pizdos!!!"}


@app.route("/api/load_kp_file", methods=['POST'])
def load_kp_file():
    
    return {"answer" : "File load succesfully broooo!!!"}

if __name__ == "__main__":
    try:
        app.run(port=8000)
    except Exception as e:
        logging.error(f"Error occurred: {e}")