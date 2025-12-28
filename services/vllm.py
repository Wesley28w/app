import os
import httpx

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID)

async def call_vllm(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            VLLM_URL,
            json={
                "model": MODEL,
                **payload,
            },
        )
        resp.raise_for_status()
        return resp.json()
