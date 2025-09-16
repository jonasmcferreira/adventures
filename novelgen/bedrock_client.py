from __future__ import annotations

import json

import boto3
from botocore.client import BaseClient


def get_client(region: str, profile: str) -> BaseClient:
    session = boto3.session.Session(profile_name=profile, region_name=region)
    return session.client("bedrock-runtime")


def invoke_text_model(
    client: BaseClient,
    model_id: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
) -> str:
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ],
    }

    response = client.invoke_model(modelId=model_id, body=json.dumps(body))
    payload = response.get("body")
    if payload is None:
        raise RuntimeError("Bedrock response missing body")

    if hasattr(payload, "read"):
        raw = payload.read()
    else:
        raw = payload

    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Failed to decode Bedrock response JSON") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected Bedrock response format: not a JSON object")

    if "content" in data:
        content = data.get("content")
        if not isinstance(content, list):
            raise RuntimeError("Bedrock response content is not a list")
        texts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text") or item.get("value")
            if isinstance(text, str):
                texts.append(text)
            elif "content" in item and isinstance(item["content"], list):
                for sub in item["content"]:
                    if isinstance(sub, dict):
                        t = sub.get("text")
                        if isinstance(t, str):
                            texts.append(t)
        if texts:
            return "".join(texts)

    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    raise RuntimeError("Bedrock response did not contain text content")
