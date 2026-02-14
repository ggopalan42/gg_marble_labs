"""Experiment 1: Generate a World Labs world from a text prompt."""

import json
import os
import sys
import time
from urllib import request, error

from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

API_BASE_URL = "https://api.worldlabs.ai/marble/v1"
WLT_API_KEY = os.environ.get("WL-FIRST-KEY")

# Text prompt to generate a world from (fill in before running)
TEXT_PROMPT = "Create a bedroom with the nightstand and a lamp/ The bedcover on the bed needs to have a cat theme. A yellow cat is sitting at the window sill, looking dolefully out the window at the full moon"


def api_fetch(path, method="GET", body=None):
    """Send an API request and parse JSON response."""
    url = f"{API_BASE_URL}/{path}"
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"WLT-Api-Key": WLT_API_KEY, "Content-Type": "application/json"}
    req = request.Request(url, data=payload, headers=headers, method=method)
    try:
        with request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body) if resp_body else {}
    except error.HTTPError as exc:
        resp_body = exc.read().decode("utf-8")
        raise RuntimeError(f"{path}: {exc.code} {resp_body}") from exc


def generate_world(text_prompt):
    """Submit a text-to-world generation request."""
    if not text_prompt:
        raise RuntimeError("TEXT_PROMPT is empty. Set it before running.")

    operation = api_fetch(
        "worlds:generate",
        method="POST",
        body={
            "world_prompt": {
                "type": "text",
                "text_prompt": text_prompt,
                "is_pano": True,
            },
            "model": "Marble 0.1-mini",
        },
    )
    return operation["operation_id"]


def poll_operation(operation_id, interval=5, timeout=600):
    """Poll an operation until it completes or times out."""
    elapsed = 0
    while elapsed < timeout:
        op = api_fetch(f"operations/{operation_id}")
        if op.get("done"):
            return op
        print(f"Operation {operation_id} still processing... ({elapsed}s)")
        time.sleep(interval)
        elapsed += interval
    raise RuntimeError(f"Operation {operation_id} timed out after {timeout}s")


def main():
    if not WLT_API_KEY:
        print("Set WLT_API_KEY in the .env file first.")
        sys.exit(1)

    prompt = TEXT_PROMPT
    if not prompt:
        print("TEXT_PROMPT is empty. Edit the file and set it before running.")
        sys.exit(1)

    print(f"Generating world from prompt: \"{prompt}\"")
    operation_id = generate_world(prompt)
    print(f"Operation submitted: {operation_id}")

    result = poll_operation(operation_id)
    world_id = result["response"]["world_id"]
    world = api_fetch(f"worlds/{world_id}")
    print("World generated:")
    print(json.dumps(world, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
