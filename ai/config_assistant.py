import json
import urllib.request
import subprocess

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3.5:4b"
NAMESPACE = "idea-board"


def get_deployment_config():
    result = subprocess.run(
        [
            "kubectl", "get", "deployment", "backend",
            "-n", NAMESPACE, "-o", "json"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    deployment = json.loads(result.stdout)

    return deployment["spec"]["template"]["spec"]


def generate_proposal(config):
    prompt = f"""
You are a Kubernetes DevOps engineer.

Review this actual backend deployment configuration:

{json.dumps(config, indent=2)}

Identify missing or improvable configurations.

Focus on:
1. CPU and memory requests/limits.
2. Readiness and liveness probes.
3. Container security context.
4. Reliability improvements.

For every proposal:
- Explain the reason.
- Show the suggested YAML configuration.
- Clearly identify assumptions.
- Do not invent application endpoints.
- Do not expose or request secrets.
- Do not apply any changes.

Return concise recommendations.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "num_predict": 400,
            "temperature": 0.2
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=600) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result.get("response", "No AI response received.")


if __name__ == "__main__":
    try:
        print("AI CONFIGURATION ASSISTANT")
        print("=" * 45)

        config = get_deployment_config()

        print("\nAnalysing actual Kubernetes configuration...\n")

        proposal = generate_proposal(config)

        print("AI CONFIGURATION PROPOSALS")
        print("=" * 45)
        print(proposal)

        print("\nNOTE: Suggestions are not automatically applied.")

    except Exception as error:
        print(f"Error: {error}")