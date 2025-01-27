from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from io import BytesIO
from table_remake import transfer_data_kp_to_spec
from parallel_oleg import make_oleg_file

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В случае, если нужно больше контроля, можно указать конкретные адреса
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = './uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
        with open(file_path, 'wb') as f:
            f.write(await file.read())

        # Передаем путь к файлу в функцию для обработки
        answer_path = transfer_data_kp_to_spec(kp_path=file_path, spec_path='spec.xlsx', output_path='answer.xlsx')

        return FileResponse(answer_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename='answer.xlsx')
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/kp")
async def list_users(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
        with open(file_path, 'wb') as f:
            f.write(await file.read())

        answer_path = make_oleg_file(file_path)

        return FileResponse(answer_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename='oleg_answer.xlsx')

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/load_kp_file")
async def load_kp_file():
    return {"answer": "File load successfully broooo!!!"}

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
