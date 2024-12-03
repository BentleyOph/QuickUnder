import os
from dotenv import load_dotenv


from thepipe.scraper import scrape_file
from thepipe.core import chunks_to_messages
from openai import OpenAI

# scrape clean markdown
chunks = scrape_file(filepath="combined.jpeg", ai_extraction=True)

# call LLM with scraped chunks
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=chunks_to_messages(chunks),
)