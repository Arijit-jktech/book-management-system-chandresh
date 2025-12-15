import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def generate_book_summary(text: str) -> str:
    """
    Generate a summary of the provided text using an AI language model.
    
    Args:
        text: The text content to summarize
        
    Returns:
        A summary string or an error message if the service is unavailable
    """
    if not settings.LLM_API_KEY or not settings.LLM_BASE_URL:
        return "AI Service not configured."

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes book content."},
            {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
        ],
        "max_tokens": 150
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error calling AI service: {e}")
            return "Error generating summary."
