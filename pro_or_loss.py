import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'

# Convert PDF to images (one image per page)
def pdf_to_images(pdf_path, output_dir):
    images = convert_from_path(pdf_path)
    image_paths = []
    
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)
    
    return image_paths

# Extract text from images using OCR (Tesseract)
def extract_text_from_images(image_paths):
    text = ""
    for image_path in image_paths:
        image = Image.open(image_path)
        text += pytesseract.image_to_string(image)
    return text

# Function to extract profit or loss and the amount
def extract_profit_or_loss(text):
    # Normalize text for easier searching
    text = text.lower()
    
    # Search for profit or loss keywords
    profit_keywords = ["profit for the year", "profit"]
    loss_keywords = ["loss for the year", "loss"]

    # Initialize variables for result
    profit_or_loss = None
    amount = None
    is_profit = False

    # Look for profit
    for keyword in profit_keywords:
        if keyword in text:
            profit_or_loss = keyword
            is_profit = True
            break

    # If no profit found, look for loss
    if profit_or_loss is None:
        for keyword in loss_keywords:
            if keyword in text:
                profit_or_loss = keyword
                is_profit = False
                break

    # Extract amount near the found keyword
    if profit_or_loss:
        # Find the position of the keyword and extract the following amount
        start_index = text.find(profit_or_loss)
        after_keyword_text = text[start_index:].splitlines()
        for line in after_keyword_text:
            # Search for a number in the text line following the keyword
            words = line.split()
            for word in words:
                try:
                    # Try to parse the number (assuming Kshs. is not included in the extracted text)
                    amount = float(word.replace(",", ""))
                    break
                except ValueError:
                    # If it’s not a valid number, keep looking
                    continue
            if amount is not None:
                break

    return is_profit, amount

# Main function to process the audited accounts
def process_audited_accounts(pdf_path, output_dir='./images'):
    # Convert PDF to images
    image_paths = pdf_to_images(pdf_path, output_dir)
    
    # Extract text from images
    extracted_text = extract_text_from_images(image_paths)
    
    # Extract profit or loss and the amount
    is_profit, amount = extract_profit_or_loss(extracted_text)
    
    return is_profit, amount

# Function to print the result
def print_profit_or_loss(is_profit, amount):
    if is_profit:
        print(f"Profit for the last year: Kshs. {amount}")
    else:
        print(f"Loss for the last year: Kshs. {amount}")

# Example usage:
if __name__ == "__main__":
    pdf_path = './audits/*.pdf'
    
    # Process the audited accounts and get the result
    is_profit, amount = process_audited_accounts(pdf_path)
    
    # Print the result
    print_profit_or_loss(is_profit, amount)
