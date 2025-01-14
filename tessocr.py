# from doctr.io import DocumentFile
# from doctr.models import ocr_predictor
from docx import Document
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import pandas as pd
import logging
from datetime import date
import tempfile
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


import os
import pytesseract
from pdf2image import convert_from_path
import glob
from PIL import Image

if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "AIzaSyC5KEY_0biZ7s7nTvhV7Endn7DZKDe3-pY"

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class DataLoader:
    def __init__(self):
        self.df = pd.DataFrame()

    def remove_rows(self, ids):
        # Remove rows with specified ids
        self.df = self.df[~self.df['id'].isin(ids)]

    def extract(self, f):
        try:
            if f.endswith(".jpg") or f.endswith(".png") or f.endswith("jpeg"):
                
                img = Image.open(f)

                text = pytesseract.image_to_string(img,lang='eng')
                today = date.today()
                text_output = str(f) + "\n" + "Today Date: " + str(today) + "\n" + "extracted text: " + "\n" + text
                return text_output

            elif f.endswith(".pdf"):
                # pages = convert_from_path(f, 500)
                # # pages = convert_from_path(f, 500,poppler_path=r"C:\poppler-24.08.0\Library\bin")
                # text = ""
                # for pageNum, imgBlob in enumerate(pages):
                #     text += f"page no.{pageNum}" + "\n"
                #     text += pytesseract.image_to_string(imgBlob,lang='eng')
                #     print("\n")
                # today = date.today()
                # text_output = str(f) + "\n" + "Today Date: " + str(today) + "\n" + "extracted text: " + "\n" + text
                # return text_output
                try:
                    text = ""
                    today = date.today()
                    
                    # Use temporary directory to handle images
                    with tempfile.TemporaryDirectory() as temp_dir:
                        pages = convert_from_path(f, dpi=150, output_folder=temp_dir)  # Lower DPI to save memory
                        for page_num, img_blob in enumerate(pages):
                            text += f"Page no. {page_num + 1}\n"
                            text += pytesseract.image_to_string(img_blob, lang='eng') + "\n"

                    text_output = f"{f}\nToday Date: {today}\nExtracted Text:\n{text}"
                    return text_output
                except Exception as e:
                    return f"Error: {str(e)}"

            elif f.endswith(".docx"):
                doc = Document(f)
                today = date.today()
                text_output = str(f) + "\n" + "Today Date: " + str(today) + "\n" 
                for paragraph in doc.paragraphs:
                    text_output += paragraph.text
                return text_output

            else:
                raise ValueError(f"Unsupported file format: {f}")

        except Exception as e:
            # Log the error and return it
            logger.error(f"Error extracting file {f}: {e}")
            return {"error": str(e)}


    def llm_parse(self,ocr_text):

        prompt_template = ChatPromptTemplate.from_template("""
        You are Document Expiry Date Tracker. You get the Document text {ocr_text} extracted from the documents. The given document text also contains today date. You help the organization to categorize
        the document into the following groups:

        Classify the document into these groups based on the today date.            
        1) Up-to-date: Documents that have not yet expired

        2) Overdue: Documents that have passed their expiration date

        3) Expiring soon: Documents that will expire within the next 30 days/ 1 month

        Provide the output in the following format (return response in JSON format):  
        
            Document name: extracted answer / "NA"

            Expiration/due date: extracted answer(in DD/MM/YYYY format) / "NA" 

            Days until expiration: extracted answer / "NA"
                                                            
            Days overdue: extracted answer(if overdue) else "NA"

            Status: extracted answer / If Expiration/due date is "NA", then "NA"
            
        Note: As mentioned in the format, if you don't get the answer fill the field with "NA"
        Note: Always return a flat JSON response with no nested keys. Do not group documents or include additional fields like "documents".
        Note: Calculate "Days until expiration" and "Days overdue" with reference to the today date
        """
        )

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",temperature=1)
        chain = ( {"ocr_text": RunnablePassthrough()}
                |prompt_template
                | llm
                | StrOutputParser()
            )

        try:
            response = chain.invoke(ocr_text)
            res = response[7:-4].strip()
            json_object = json.loads(res)
            return json_object
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"error": "Invalid LLM response"}
    
    def add_rows(self,filepaths):
        for file in filepaths:
            extracted_text = self.extract(file)
            json_response = self.llm_parse(extracted_text)
            # print(type(json_response))
            self.df.append(json_response)
        return self.df
    
    def json_to_df(self):
        json_res = self.df
        df1 = pd.DataFrame(json_res)
        # self.df.clear()
        return df1
    
    # def remove_row(self):
    #     pass
        


# text = extract("Aniesh_Passport.pdf")
# res = llm_parse(text)
# print(res[7:-4])

# obj2 = DataLoader()
# data = obj2.extract(r"C:\Users\Anidhinesh\Documents\Aniesh Docs\E-Docs\Aniesh_Passport.pdf")

# data = obj.add_row("Aniesh_Passport.pdf")
# # obj.add_row("temp_Aniesh e-pan.pdf")

# # data = obj.json_to_df()
# print(data)
