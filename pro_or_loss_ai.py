import os
import json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI
from pdftotext import pdf_to_images, combine_images
from pro_or_loss import extract_text_from_images

load_dotenv()

# Initialize the OpenAI API client
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv('OPENAI_PROJECT_ID')
client = OpenAI(
    organization='org-8VjUpT7VbQkqQsqzHTLoa1h0',
    project=project_id
)

class FinancialData(BaseModel):
    year: int = Field(..., description="Year of the financial statement")
    revenue: float = Field(..., description="Revenue in Kshs.")
    expenses: float = Field(..., description="Expenses in Kshs.")
    net_profit: float = Field(..., description="Net profit or loss in Kshs.")

class FinancialReview(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    financial_data: List[FinancialData]
    profit_or_loss: str = Field(..., description="Indicates if the company made a profit or loss overall.")
    risk_analysis: str = Field(..., description="An analysis of the financial risks of the company.")
    comments: str = Field(..., description="General comments about the company's financial health.")

def extract_financial_data(text):
    system_prompt = """
    You are an expert at extracting financial data from financial statements.
    
    1. Extract revenue, expenses, and net profit for each year from the given financial statement. 
    2. Group the extracted data for each year, including the year, revenue, expenses, and net profit.
    3. Output the data as JSON in the following structure:
    
    {
      "company_name": "Company ABC",
      "financial_data": [
        {"year": 2022, "revenue": 5000000, "expenses": 3000000, "net_profit": 2000000},
        {"year": 2023, "revenue": 6000000, "expenses": 4000000, "net_profit": 2000000}
      ],
      "profit_or_loss": "Profit",  # or "Loss"
      "risk_analysis": "An assessment of financial risks based on revenue, profit, and loss trends.",
      "comments": "General comments about the company, its financial position, and overall performance."
    }

    4. If a financial statement does not contain relevant data, output an empty JSON object.
    5. If a field is missing in the financial statement, mark it as null in the output.
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        response_format=FinancialReview,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"extract the financial data from the following text:\n{text}"},
                ]
            }
        ],
    )
    
    return response.choices[0].message.parsed

def review_financial_statements(pdf_paths: List[str], output_file: str):
    extracted_data = []
    
    for pdf_path in pdf_paths:
        # Convert each PDF to images
        print(f"Processing {pdf_path}...")
        image_directory = './images'
        image_paths = pdf_to_images(pdf_path, image_directory)
        
        # Extract text from images
        extracted_text = extract_text_from_images(image_paths)
        
        # Process the extracted text into financial data
        financial_data = extract_financial_data(extracted_text)
        
        if financial_data:
            extracted_data.append(financial_data.dict())  # financial_data should already be a dictionary or Pydantic object
    
    # Save the extracted data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([data for data in extracted_data], f, ensure_ascii=False, indent=4)

    print(f"Financial data extracted and saved to {output_file}")

def main():
    # List of financial statement PDFs
    pdf_paths = ['./audits/audits.pdf', './audits/audits2.pdf']
    
    # Output file for extracted financial data
    output_file = 'financial_review.json'
    
    # Review financial statements
    review_financial_statements(pdf_paths, output_file)

if __name__ == "__main__":
    main()
