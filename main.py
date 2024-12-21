from fastapi import FastAPI, File, UploadFile
from typing import List
import shutil
from pydantic import BaseModel
from ocr import DataLoader
import uvicorn

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()
data_obj = DataLoader()

@app.get("/")
def get_status():
    return "Status: OK"

@app.post("/process-multiple-files")
async def process_multiple_files(files: List[UploadFile] = File(...)):
    file_paths = []

    for file in files:
        # Save each file temporarily in the backend
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        # Append the file path to the list
        file_paths.append(temp_file_path)

    return file_paths

# @app.post("/get-df")
# async def get_df(filepaths: List[str]):
#     data_obj.add_rows(filepaths)
#         # print(type(df[0]))
    
#     df1 = data_obj.json_to_df()
#     logger.debug("Data before serialization: %s", df1.to_dict(orient="records"))

#     return df1.to_dict(orient="records")
#     # return df
@app.post("/get-df")
async def get_df(filepaths: List[str]):
    try:
        if not isinstance(filepaths, list) or not all(isinstance(path, str) for path in filepaths):
            return {"error": "Invalid file paths format"}

        # Process files and create dataframe
        data_obj.add_rows(filepaths)
        df1 = data_obj.json_to_df()
        
        logger.debug("Data before serialization: %s", df1.to_dict(orient="records"))
        return df1.to_dict(orient="records")  # Return as JSON-serializable dict
    except Exception as e:
        logger.error(f"Error in /get-df: {e}")
        return {"error": str(e)}






