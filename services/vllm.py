import os
import httpx

VLLM_BASE_URL = os.environ["VLLM_BASE_URL"].rstrip("/")
VLLM_MODEL = os.environ["VLLM_MODEL"]

VLLM_CHAT_URL = f"{VLLM_BASE_URL}/v1/chat/completions"


async def chat_with_vllm(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(
            VLLM_CHAT_URL,
            json={
                "model": VLLM_MODEL,
                **payload,
            },
        )
        response.raise_for_status()
        return response.json()
