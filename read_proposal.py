from openai import OpenAI
import fitz  # PyMuPDF
import io
import os
from PIL import Image
import base64
import json
from dotenv import load_dotenv
from pdftotext import pdf_to_images, combine_images,encode_image
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv('OPENAI_PROJECT_ID')
client = OpenAI(
  organization='org-8VjUpT7VbQkqQsqzHTLoa1h0',
  project= project_id
)


class IndemnityAndExcess(BaseModel):
    indemnity: float = Field(..., description="Indemnity amount in Kshs.")
    excess: float = Field(..., description="Excess amount in Kshs.")

class ExtraCovers(BaseModel):
    libel_and_slander: bool = Field(..., description="Coverage for defamation,libel and slander")
    loss_of_documents: bool = Field(..., description="Coverage for loss of documents (Legal liability only)")
    dishonesty_of_employees: bool = Field(..., description="Coverage for dishonesty of employees and retroactive errors and ommisions ")

class Revenues(BaseModel):
    year_2022: float = Field(..., description="Revenue for the year 2022 in Kshs.")
    year_2023: float = Field(..., description="Revenue for the year 2023 in Kshs.")
    estimated_income: float = Field(..., description="Estimated income in Kshs.")

class ProposalForm(BaseModel):
    name_of_reinsured: str = Field(..., description="Name of the re-insured")
    name_of_insured: str = Field(..., description="Name of the insured")
    occupation_of_insured: str = Field(..., description="Occupation of the insured")
    period_of_cover: int = Field(..., description="Period of cover (year)")
    number_of_business_partners: int = Field(..., description="Number of business partners")
    number_of_staff: int = Field(..., description="Number of qualified/unqualified staff employed")
    indemnity_and_excess: IndemnityAndExcess
    extra_covers: ExtraCovers
    revenues: Revenues


def extract_proposal_data(base64_image):
    base64_image = encode_image(base64_image)
    system_prompt = f"""
    You are an expert at structured data extraction especially insurance proposal forms data from PDFs.You will be given unstructured text from the pdf and should convert it into the given structure

    1. Please extract the data in this insurance proposal form, grouping data according to theme/sub groups, and then output into JSON.

    2. Please keep the keys and values of the JSON in the original language and format as found in the form.

    3. The type of data you might encounter in the proposal form includes but is not limited to: re-insured information, insured details, occupation, period of cover, business partners, staff information, indemnity and excess details, extra covers, and revenue figures.

    4. If the page contains no relevant data, please output an empty JSON object and do not make up any data.

    5. If there are blank data fields in the form, please include them as "null" values in the JSON object.

    6. If there are tables or lists in the form (e.g. revenue data), capture all rows and columns in the JSON object. Even if a column is blank, include it as a key in the JSON object with a null value.

    7. If a row is blank, denote missing fields with "null" values.

    8. Don't interpolate or make up data.

    9. Please maintain the structure of grouped data, such as extra covers and revenues for each year, in the JSON object.

    Name of re-insured: Look for this in the document title (e.g., something assurance/insurance company).
Name of insured: Pay very close attention to the handwritten company name. Examine the first letter carefully - NOTE !!it may look like a 'P' but could actually be an 'F'. For example, "Fekan Howell LLP" might be mistaken for "Pekan Howell LLP". Analyze the letter formation closely and provide your most accurate reading.
Occupation of insured: This information is typically found in the first few lines of the form, where the company name is listed/Detailed description of the business.
Period of cover: Find the year written next to DATE at the bottom of the form (cannot be less than 2024)
Revenues for each year: Carefully look for a section that lists turnover over the past two years(strictly 2022 and 2023) and projected revenue for the forthcoming year.Look at individual digits and ensure you are not mistaking a 1 for a 7, or a 1 for a for 4 ,or a 0 for an 8 ,a 4 for a 9 etc.
Number of business partners :A section that lists partners of the firm. 1 count for each name listed please.(YOU GET 200% BONUS COMPUTE IF YOU GET  THIS RIGHT)Look at positions listed for further hint
Number of qualified/unqualified staff employed.
Indemnity and excess required: This information is typically found in a section about insurance coverage details.
State any extra covers required: Look for additional insurance options or coverages mentioned at the last page of the form.

NOTE : dishonesty of employees includes retroactive errors and ommisions
Defamation is the same as slander 
"""

    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        response_format= ProposalForm,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "extract the data in this proposal form and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ],
    )
    return response.choices[0].message.parsed 



def main():
    # Proposal form PDF path
    proposal_pdf_path = './proposals/proposal_form.pdf'
    image_directory = './images'

    # 1. Convert proposal form PDF to images
    print("Converting proposal PDF to images...")
    image_paths = pdf_to_images(proposal_pdf_path, image_directory)
    
    # 2. Combine images into one
    print("Combining proposal form images...")
    combined_image = combine_images(image_paths)

    print("Extracting ...")
    extracted = extract_proposal_data(combined_image)

    #save extracted which is json 
    output_filename = 'extracted.json'
    with open( output_filename, 'w', encoding='utf-8') as f:
        json.dump(extracted.dict(),f,ensure_ascii=False,indent=4)
    
    print(extracted)
    print("Extracted data saved")

    


if __name__ == "__main__":
    main()

