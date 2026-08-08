import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CLASSIFICATION_PROMPT = """You are classifying YouTube comments to find content suggestions for a creator's next video.

For each comment below, classify it into exactly one category:
- SUGGESTION: proposes, requests, or hints at a topic/format for a future video
- REACTION: praise, criticism, or general commentary about the current video
- QUESTION: asks something about the current video's content
- SPAM: promotional, bot-like, off-topic, or engagement-bait

Return ONLY valid JSON, no preamble, no markdown fences:
[{{"id": "<comment_id>", "category": "SUGGESTION|REACTION|QUESTION|SPAM", "confidence": 0.0}}]

Comments:
{comments}
"""

def classify_batch(comments: list[dict]) -> list[dict]:
    """comments: [{'id': str, 'body': str}, ...] - max ~30 per call"""
    formatted = "\n".join(f"{c['id']}: {c['body']}" for c in comments)
    prompt = CLASSIFICATION_PROMPT.format(comments=formatted)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()

    # Remove markdown fences
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        raw_text = "\n".join(lines).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("Invalid JSON returned by Claude:")
        print(raw_text)
        raise ValueError("Claude did not return valid JSON") from e

def classify_comments_in_batches(comments: list[dict], batch_size: int = 30) -> list[dict]:
    results = []
    for i in range(0, len(comments), batch_size):
        batch = comments[i:i + batch_size]
        results.extend(classify_batch(batch))
    return results