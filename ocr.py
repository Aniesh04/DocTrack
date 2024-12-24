from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from docx import Document
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import pandas as pd

if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "AIzaSyC5KEY_0biZ7s7nTvhV7Endn7DZKDe3-pY"

class DataLoader:
    def __init__(self):
        self.df = []

    def extract(self,f):
        # for f in files:
        if f.endswith(".jpg") or f.endswith(".png") or f.endswith("jpeg"):
            model = ocr_predictor(pretrained=True)
            doc = DocumentFile.from_images(f)
            # Analyze
            result = model(doc)
            text_output = str(f) 
            text_output += "/n" + result.render()
            # print(text_output)
            
            return text_output
        
        elif f.endswith(".pdf"):
            doc = DocumentFile.from_pdf(f)
            model = ocr_predictor(pretrained=True)
            result = model(doc)
            text_output = str(f) 
            text_output += "/n" + result.render()
            return text_output

        elif f.endswith(".docx"):
            doc = Document(f)
            text_output = str(f) + "/n"
            for paragraph in doc.paragraphs:
                text_output += paragraph.text
            return text_output



    def llm_parse(self,ocr_text):

        prompt_template = ChatPromptTemplate.from_template("""
        You are Document Expiry Date Tracker. You get the Document text {ocr_text} extracted from the documents. You help the organization to categorize
        the document into the following groups:
        1) Up-to-date: Documents that have not yet expired

        2) Overdue: Documents that have passed their expiration date

        3) Expiring soon: Documents that will expire within the next 30 days

        Provide the output in the following format (return response in JSON format):  
        
            Document name: extracted answer / "NA"

            Expiration/due date: extracted answer / "NA"

            Days until expiration: extracted answer / "NA"
                                                            
            Days overdue: extracted answer(if overdue) else "NA"

            Status: extracted answer / "NA"    
            
        Note: As mentioned in the format, if you don't get the answer fill the field with "NA"
        Note: Always return a flat JSON response with no nested keys. Do not group documents or include additional fields like "documents".

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
        self.df.clear()
        return df1

    # def json_to_df(self):
    #     from pandas import json_normalize

    #     # Debug: Print raw JSON responses
    #     print("Raw JSON responses:", self.df)

    #     try:
    #         # Flatten nested JSON using json_normalize
    #         flattened_responses = []
    #         for item in self.df:
    #             if "documents" in item:
    #                 # If nested "documents" key exists, normalize it
    #                 nested_docs = item.pop("documents", [])
    #                 for nested_doc in nested_docs:
    #                     flattened_item = {**item, **nested_doc}
    #                     flattened_responses.append(flattened_item)
    #             else:
    #                 flattened_responses.append(item)

    #         # Create a DataFrame from the flattened list
    #         df1 = pd.DataFrame(flattened_responses)

    #         # Debug: Print the cleaned DataFrame
    #         print("Flattened DataFrame:\n", df1.head())

    #         # Handle missing values (replace NaN with "NA")
    #         df1 = df1.fillna("NA")

    #         # Clear the internal data list
    #         self.df.clear()
    #         return df1
    #     except Exception as e:
    #         print(f"Error creating DataFrame: {e}")
    #         return pd.DataFrame()  # Return an empty DataFrame on failure


    
    # def remove_row(self):
    #     pass
        




# text = extract("Aniesh_Passport.pdf")
# res = llm_parse(text)
# print(res[7:-4])

# obj = DataLoader()

# data = obj.add_row("Aniesh_Passport.pdf")
# # obj.add_row("temp_Aniesh e-pan.pdf")

# # data = obj.json_to_df()
# print(data)