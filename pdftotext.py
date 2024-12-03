from PIL import Image
import os
import base64
import requests
from pdf2image import convert_from_path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
openai_key = os.getenv('OPENAI_API_KEY')
project_id = os.getenv('OPENAI_PROJECT_ID')

# Convert PDF to images (one image per page)
def pdf_to_images(pdf_path, output_dir):
    # Convert PDF pages to images and save them
    images = convert_from_path(pdf_path)
    image_paths = []
    
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)
    
    return image_paths

# Combine all images into one single image (vertically)
def combine_images(image_paths):
    images = [Image.open(image_path) for image_path in image_paths]
    
    # Calculate the total width and total height for the final combined image
    total_width = max(image.width for image in images)
    total_height = sum(image.height for image in images)
    
    # Create a blank canvas to paste the images
    combined_image = Image.new('RGB', (total_width, total_height))
    
    # Paste each image one below the other
    y_offset = 0
    for image in images:
        combined_image.paste(image, (0, y_offset))
        y_offset += image.height
    
    combined_image.save('combined.jpeg')
    return combined_image

# Encode image to Base64
def encode_image(image):
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# # Send the combined image to OpenAI API for text extraction
# def process_combined_image(combined_image):
#     base64_image = encode_image(combined_image)
    
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {openai_key}"
#     }

#     payload = {
#             "model": "gpt-4o",
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": """The following are to be provided from the proposal form :
# Name of re-insured: Look for this in the document title (e.g., something assurance/insurance company).
# Name of insured: Pay very close attention to the handwritten company name. Examine the first letter carefully - it may look like a 'P' but could actually be an 'F'. For example, "Fekan Howell LLP" might be mistaken for "Pekan Howell LLP". Analyze the letter formation closely and provide your most accurate reading.
# Occupation of insured: This information is typically found in the first few lines of the form, where the company name is listed/Detailed description of the business.
# Period of cover: Find the year written next to DATE at the bottom of the form (cannot be less than 2024)
# Revenues for each year: Carefully look for a section that lists turnover over the past two years(strictly 2022 and 2023) and projected revenue for the forthcoming year.Look at individual digits and ensure you are not mistaking a 1 for a 7, or a 1 for a for 4 ,or a 0 for an 8 ,a 4 for a 9 etc.
# Number of business partners :A section that lists partners of the firm. 1 count for each name listed please.(YOU GET 200% BONUS COMPUTE IF YOU GET  THIS RIGHT)Look at positions listed for further hint
# Number of qualified/unqualified staff employed.
# Indemnity and excess required: This information is typically found in a section about insurance coverage details.
# State any extra covers required: Look for additional insurance options or coverages mentioned at the last page of the form.


# ENSURE ACCURACY FOR A BONUS IN COMPUTE 

# Provide answers in this format 
# Name of re-insured: *insert name here*
# Name of insured: *insert name here*
# Occupation of insured: *insert occupation here*
# Period of cover: *insert year here*
# Number of business partners: *insert number here*
# Number of qualified/unqualified staff employed: *insert number*
# Indemnity and excess required:
#     Indemnity: Kshs. *insert amount*
#     Excess: Kshs. *insert amount*
# Extra covers required:
#   - Yes/no, for Libel and slander
#   - Yes/no, for Loss of documents (Legal liability only)
#   - Yes/no, for Dishonesty of Employees

# Revenues for each year:
# 2022: Kshs. *insert amount*
# 2023: Kshs. *insert amount*
# *Estimated income*: Kshs. *insert amount*
# """
#                         },
#                         {
#                             "type": "image_url",
#                             "image_url": {
#                                 "url": f"data:image/jpeg;base64,{base64_image}"
#                             }
#                         },
#                     ]
#                 }
#             ],
#             "max_tokens": 300
#         }

#     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

#     if response.status_code == 200:
#         try:
#             # Extract content from response
#             data = response.json()
#             content = data.get('choices')[0].get('message').get('content')
#             return content
#         except (IndexError, AttributeError, KeyError) as e:
#             print(f"Error extracting content: {e}")
#             print(f"Response received: {response.json()}")
#     else:
#         print(f"Failed to process the image. Status code: {response.status_code}")
#         print(f"Response: {response.text}")

# # Main function to execute the whole pipeline
# def main():
#     # Set PDF path and output directories
#     pdf_path = './facultative underwriting/proposal_form.pdf'
#     image_directory = './images'
    
#     # Ensure the image directory exists
#     if not os.path.exists(image_directory):
#         os.makedirs(image_directory)
    
#     # Convert PDF to images and save them to the image directory
#     print("Converting PDF to images...")
#     image_paths = pdf_to_images(pdf_path, image_directory)
    
#     # Combine the images into one
#     print("Combining images into one...")
#     combined_image = combine_images(image_paths)
    
#     # Process the combined image and extract text
#     print("Processing combined image for text extraction...")
#     content = process_combined_image(combined_image)
    
#     # Save the extracted content to a text file
#     if content:
#         with open('output.txt', 'w', encoding='utf-8') as file:
#             file.write(content)
#         print("Extracted content saved to output.txt")
    
# if __name__ == "__main__":
#     main()
