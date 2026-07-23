from openai import OpenAI

def generate_embeddings(text: str) -> list:
    """Generate embeddings using OpenAI text-embedding-3-small."""
    try:
        client = OpenAI()
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []
