import os
import time
import json
import requests
from typing import Generator, Tuple, Optional
from src.generator.prompts import RAG_SYSTEM_PROMPT

class LLMResponseGenerator:
    """Native LLM Generator using Groq API directly without LangChain."""

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    @classmethod
    def _get_api_key(cls, api_key: Optional[str] = None) -> str:
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key or not key.strip():
            raise ValueError("Groq API Key is missing. Please provide it in sidebar or .env file.")
        return key.strip()

    @classmethod
    def generate_response(
        cls,
        model_name: str,
        query: str,
        context: str,
        api_key: Optional[str] = None
    ) -> Tuple[str, float]:
        """Generate response synchronously using Groq API directly."""
        key = cls._get_api_key(api_key)
        prompt = RAG_SYSTEM_PROMPT.format(context=context, question=query)

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        start_time = time.time()
        resp = requests.post(cls.GROQ_API_URL, headers=headers, json=payload, timeout=30)
        gen_time_ms = (time.time() - start_time) * 1000.0

        if resp.status_code != 200:
            raise RuntimeError(f"Groq API Error ({resp.status_code}): {resp.text}")

        data = resp.json()
        answer_text = data["choices"][0]["message"]["content"]
        return answer_text, gen_time_ms

    @classmethod
    def stream_response(
        cls,
        model_name: str,
        query: str,
        context: str,
        api_key: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream response tokens from Groq API directly."""
        key = cls._get_api_key(api_key)
        prompt = RAG_SYSTEM_PROMPT.format(context=context, question=query)

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "stream": True
        }

        resp = requests.post(cls.GROQ_API_URL, headers=headers, json=payload, stream=True, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Groq API Error ({resp.status_code}): {resp.text}")

        for line in resp.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: ") and line_str != "data: [DONE]":
                    try:
                        chunk_json = json.loads(line_str[6:])
                        delta = chunk_json["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]
                    except Exception:
                        pass
