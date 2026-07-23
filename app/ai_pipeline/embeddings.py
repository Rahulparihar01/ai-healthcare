import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", "mock-key"))

async def generate_embedding(text: str) -> list[float]:
    """
    Generates a 1536-dimensional float vector for the input text using text-embedding-3-small.
    """
    try:
        response = await client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return [0.0] * 1536  # Return zero vector as fallback
