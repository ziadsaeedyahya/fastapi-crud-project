from pydantic import BaseModel
from typing import Dict, Any

class LLMRequest(BaseModel):
    prompt: str

class TokenUsage(BaseModel):
    input: int
    output: int
    total: int

class LLMMetadata(BaseModel):
    tokens: TokenUsage
    model: str
    finish_reason: str

class LLMResponse(BaseModel):
    text: str
    meta: LLMMetadata