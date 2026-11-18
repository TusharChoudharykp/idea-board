import json
import subprocess
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3.5:4b"
NAMESPACE = "idea-board"


def run_kubectl(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return f"Not available: {result.stderr.strip()}"

    return result.stdout


def collect_metrics():
    commands = {
        "pods": [
            "kubectl", "get", "pods",
            "-n", NAMESPACE, "-o", "wide"
        ],
        "deployments": [
            "kubectl", "get", "deployments",
            "-n", NAMESPACE
        ],
        "cpu_memory_usage": [
            "kubectl", "top", "pods",
            "-n", NAMESPACE
        ],
        "node_usage": [
            "kubectl", "top", "nodes"
        ]
    }

    return {
        name: run_kubectl(command)
        for name, command in commands.items()
    }


def analyze_metrics(data):
    prompt = f"""
You are a Kubernetes DevOps engineer.

Analyse this actual Kubernetes health and metrics data:

{json.dumps(data, indent=2)}

Provide:
1. Overall cluster application health.
2. Pod and deployment problems, if any.
3. CPU and memory usage observations, if available.
4. Potential resource or reliability risks.
5. Recommended troubleshooting commands or improvements.

Rules:
- Use only the supplied evidence.
- Do not invent CPU or memory values.
- If metrics are unavailable, clearly state that.
- Do not assume high usage without evidence.
- Do not execute commands.
- Keep the analysis concise.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "num_predict": 300,
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
        print("AI HEALTH AND METRICS ASSISTANT")
        print("=" * 45)

        print("\nCollecting Kubernetes health and metrics...")

        data = collect_metrics()

        print("\nAnalysing collected data with AI...\n")

        analysis = analyze_metrics(data)

        print("AI HEALTH AND METRICS ANALYSIS")
        print("=" * 45)
        print(analysis)

        print("\nNOTE: No Kubernetes resources were modified.")

    except Exception as error:
        print(f"Error: {error}")