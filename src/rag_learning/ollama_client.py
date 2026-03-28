from __future__ import annotations

import json
from urllib import error, request


class OllamaClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def embed(self, model: str, text: str) -> list[float]:
        payload = {"model": model, "input": text}
        try:
            response = self._post_json("/api/embed", payload)
            embeddings = response.get("embeddings")
            if embeddings:
                return embeddings[0]
        except RuntimeError as exc:
            if "HTTP 404" not in str(exc):
                raise

        legacy_payload = {"model": model, "prompt": text}
        response = self._post_json("/api/embeddings", legacy_payload)
        embedding = response.get("embedding")
        if not embedding:
            raise RuntimeError("Ollama did not return embeddings.")
        return embedding

    def chat(self, model: str, prompt: str) -> str:
        payload = {
            "model": model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful internal engineering assistant. "
                        "Answer only from the provided context. "
                        "If the context is insufficient, say so clearly."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        response = self._post_json("/api/chat", payload)
        message = response.get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("Ollama did not return a chat response.")
        return content.strip()

    def _post_json(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url=f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise RuntimeError(
                f"Ollama request failed with HTTP {exc.code}. Check the endpoint and model names."
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                "Could not reach Ollama. Make sure Ollama is running and the model names are correct."
            ) from exc