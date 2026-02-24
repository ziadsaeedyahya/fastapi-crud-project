import cohere
from app.core.config import settings

class CohereEmbeddingClient:
    def __init__(self):
        # بنستخدم الكي اللي متعرف عندك فعلاً في الـ settings
        self.client = cohere.Client(api_key=settings.COHERE_API_KEY)

    def get_embeddings(self, texts: list[str], input_type: str = "search_document"):
        try:
            response = self.client.embed(
                texts=texts,
                model='embed-v4.0',
                input_type=input_type,
                embedding_types=['float']
            )
            return response.embeddings.float
        except Exception as e:
            print(f"❌ Cohere Embedding Error: {str(e)}")
            return None

embedding_client = CohereEmbeddingClient()