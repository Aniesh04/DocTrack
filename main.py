from fastapi import FastAPI, File, UploadFile
from typing import List
import shutil
# from pydantic import BaseModel
from tessocr import DataLoader
# import uvicorn
from db import DatabaseHandler
import pandas as pd

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
db_handler = DatabaseHandler()
data_obj = DataLoader()

@app.get("/")
async def get_status():
    return "Status: OK"

#local
# @app.post("/process-multiple-files")
# async def process_multiple_files(files: List[UploadFile] = File(...)):
#     file_paths = []

#     for file in files:
#         # Save each file temporarily in the backend
#         temp_file_path = f"temp_{file.filename}"
#         with open(temp_file_path, "wb") as temp_file:
#             shutil.copyfileobj(file.file, temp_file)

#         # Append the file path to the list
#         file_paths.append(temp_file_path)

#     return file_paths
@app.post("/process-multiple-files")
async def process_multiple_files(files: List[UploadFile] = File(...)):
    file_paths = []

    for file in files:
        # Save each file temporarily on the backend
        temp_file_path = f"/tmp/{file.filename}"  # Save in backend's /tmp/ directory
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        file_paths.append(temp_file_path)

    return file_paths

@app.post("/get-df")
async def get_df(filepaths: List[str]):
    try: 
        data_obj.add_rows(filepaths)
            # print(type(df[0]))
        
        df1 = data_obj.json_to_df()
        logger.debug("Data before serialization: %s", df1.to_dict(orient="records"))

        return df1.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error in /get-df: {e}")
        return {"error": str(e)}
    # return df
# @app.post("/get-df")
# async def get_df(filepaths: List[str]):
#     try:
#         if not isinstance(filepaths, list) or not all(isinstance(path, str) for path in filepaths):
#             return {"error": "Invalid file paths format"}

#         # Process files and create dataframe
#         data_obj.add_rows(filepaths)
#         df1 = data_obj.json_to_df()
        
#         logger.debug("Data before serialization: %s", df1.to_dict(orient="records"))
#         return df1.to_dict(orient="records")  # Return as JSON-serializable dict
#     except Exception as e:
#         logger.error(f"Error in /get-df: {e}")
#         return {"error": str(e)}
# @app.post("/get-df")
# async def get_df(filepaths: List[str]):
#     try:
#         if not isinstance(filepaths, list) or not all(isinstance(path, str) for path in filepaths):
#             return {"error": "Invalid file paths format"}

#         # Process files and create dataframe
#         data_obj.add_rows(filepaths)
#         df1 = data_obj.json_to_df()

#         # Convert the DataFrame to a list of dictionaries
#         response = df1.to_dict(orient="records")
#         return response if response else []
#     except Exception as e:
#         logger.error(f"Error processing files: {e}")
#         return {"error": f"Failed to process file: {e}"}




# @app.post("/save-df")
# async def save_df(filepaths: List[str]):
#     try:
#         data_obj.add_rows(filepaths)
#         df1 = data_obj.json_to_df()

#         # Save DataFrame to the database
#         response = db_handler.insert_dataframe(df1)
#         return response
#     except Exception as e:
#         return {"error": str(e)}

@app.get("/get-records")
async def get_records():
    """
    Retrieve all records from the database.
    """
    try:
        records = db_handler.get_all_records()
        return records
    except Exception as e:
        return {"error": str(e)}

@app.post("/update-records")
async def update_records(data: List[dict]):
    """
    Update database records with modified data from the Streamlit editor.
    """
    try:
        df = pd.DataFrame(data)
        response = db_handler.update_records(df)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.post("/clear-database")
async def clear_database():
    """
    Endpoint to clear all records from the database.
    """
    try:
        response = db_handler.clear_all_records()
        data_obj.df.clear()
        return response
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return {"error": str(e)}

@app.post("/remove-rows")
async def remove_rows(ids: List[int]):
    """
    Remove rows with specified IDs from the in-memory DataFrame.
    """
    try:
        data_obj.remove_rows(ids)
        return {"status": "success", "removed_ids": ids}
    except Exception as e:
        logger.error(f"Error removing rows: {e}")
        return {"error": str(e)}
