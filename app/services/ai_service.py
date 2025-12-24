import httpx
import logging
import asyncio
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

async def generate_book_summary(text: str, max_retries: int = 3) -> str:
    """
    Generate a summary of the provided text using an AI language model.
    Includes retry logic with exponential backoff.
    
    Args:
        text: The text content to summarize
        max_retries: Maximum number of retry attempts
        
    Returns:
        A summary string or an error message if the service is unavailable
    """
    if not settings.LLM_API_KEY or not settings.LLM_BASE_URL:
        logger.warning("AI Service not configured - missing API key or base URL")
        return "AI Service not configured."

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes book content."},
            {"role": "user", "content": f"Please summarize the following text:\\n\\n{text}"}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Calling AI service (attempt {attempt + 1}/{max_retries})")
                response = await client.post(
                    f"{settings.LLM_BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                # Validate response structure
                data = response.json()
                if "choices" not in data or len(data["choices"]) == 0:
                    raise ValueError("Invalid response structure from AI service")
                
                summary = data["choices"][0]["message"]["content"].strip()
                logger.info("Successfully generated AI summary")
                return summary
                
        except httpx.TimeoutException as e:
            logger.warning(f"AI service timeout (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("AI service timeout - max retries exceeded")
                return "Error: AI service timeout. Please try again later."
                
        except httpx.HTTPStatusError as e:
            logger.error(f"AI service HTTP error: {e.response.status_code} - {e.response.text}")
            return f"Error: AI service returned status {e.response.status_code}"
            
        except ValueError as e:
            logger.error(f"Invalid AI service response: {e}")
            return "Error: Invalid response from AI service"
            
        except Exception as e:
            logger.error(f"Unexpected error calling AI service: {e}", exc_info=True)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                return "Error generating summary. Please try again later."
    
    return "Error generating summary after multiple attempts."
