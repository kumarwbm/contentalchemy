import os
import uuid
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI

from src.core.config import get_settings

IMAGES_DIR = "generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)


def _enhance_prompt(raw_prompt: str) -> str:
    """Enhance a raw prompt for better marketing image generation."""
    return (
        f"{raw_prompt}. "
        "Professional marketing photography style, clean background, "
        "high resolution, suitable for business use, vibrant but not garish."
    )


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=6))
def _generate(prompt: str, model: str, size: str = "1024x1024") -> str:
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
    )
    return response.data[0].url


def _download_image(url: str) -> str:
    filename = f"{IMAGES_DIR}/{uuid.uuid4().hex}.png"
    with httpx.Client(timeout=30) as client:
        r = client.get(url)
        r.raise_for_status()
        with open(filename, "wb") as f:
            f.write(r.content)
    return filename


def generate_image(raw_prompt: str) -> dict:
    """
    Generate an image with DALL-E 3, falling back to DALL-E 2 on failure.
    Returns: {url, local_path, prompt_used, model_used, error}
    """
    settings = get_settings()
    enhanced = _enhance_prompt(raw_prompt)

    for model in [settings.image_model, settings.image_fallback_model]:
        try:
            url = _generate(enhanced, model)
            local_path = _download_image(url)
            return {
                "url": url,
                "local_path": local_path,
                "prompt_used": enhanced,
                "model_used": model,
                "error": None,
            }
        except Exception as e:
            last_error = str(e)
            continue

    return {
        "url": None,
        "local_path": None,
        "prompt_used": enhanced,
        "model_used": None,
        "error": f"All image providers failed: {last_error}",
    }
