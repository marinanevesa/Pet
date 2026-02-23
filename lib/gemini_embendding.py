import os
from google import genai
from google.genai import types

from dotenv import load_dotenv

def gerarEmbedding(question):
    load_dotenv()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
    )
    
    client.close()
    
    return result
