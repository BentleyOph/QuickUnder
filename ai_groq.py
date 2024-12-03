from groq import Groq
import base64
from dotenv import load_dotenv
import os

load_dotenv()

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "combined.jpeg"
# Getting the base64 string
base64_image = encode_image(image_path)

client = Groq(
    api_key = os.environ.get("GROQ_API_KEY"),
  )

prompt = """You are an expert at extracting necessary data from proposal forms.
Output it in json in this format.For example
{
    "name_of_reinsured": "First Assurance Company Ltd.",
    "name_of_insured": "Pekan Howell LLP",
    "occupation_of_insured": "Audit, Tax, and Advisory Services (Certified Public Accountants)",
    "period_of_cover": 2024,
    "number_of_business_partners": 3,
    "number_of_staff": 7,
    "indemnity_and_excess": {
        "indemnity": 100000000.0,
        "excess": 2000000.0
    },
    "extra_covers": {
        "libel_and_slander": true,
        "loss_of_documents": true,
        "dishonesty_of_employees": true
    },
    "revenues": {
        "year_2022": 7000000.0,
        "year_2023": 7300000.0,
        "estimated_income": 10000000.0
    }
}
"""

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"{prompt}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    response_format={"type": "json_object"},
    stop=None,
    model="llama-3.2-11b-vision-preview",
)

print(chat_completion.choices[0].message.content)