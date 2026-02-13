from app.llm_clients.llm_manager import llm_manager

class LLMService:
    @staticmethod
    def ask_ai(prompt: str):
        # بننادي المانجر اللي عملناه وهو بيتصرف مع Cohere
        return llm_manager.get_response(prompt=prompt)