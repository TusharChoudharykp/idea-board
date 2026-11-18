import json
import subprocess
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3.5:4b"
NAMESPACE = "idea-board"
DEPLOYMENT = "backend"


def run_kubectl(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return f"Command error: {result.stderr}"

    return result.stdout


def collect_cluster_data():
    commands = {
        "deployment": [
            "kubectl", "get", "deployment", DEPLOYMENT,
            "-n", NAMESPACE, "-o", "wide"
        ],
        "rollout_history": [
            "kubectl", "rollout", "history",
            f"deployment/{DEPLOYMENT}", "-n", NAMESPACE
        ],
        "rollout_status": [
            "kubectl", "rollout", "status",
            f"deployment/{DEPLOYMENT}", "-n", NAMESPACE
        ],
        "replicasets": [
            "kubectl", "get", "replicasets",
            "-n", NAMESPACE
        ],
        "pods": [
            "kubectl", "get", "pods",
            "-n", NAMESPACE
        ]
    }

    return {
        name: run_kubectl(command)
        for name, command in commands.items()
    }


def analyze_rollback(data):
    prompt = f"""
You are a Kubernetes DevOps engineer.

Analyse this actual Kubernetes deployment information:

{json.dumps(data, indent=2)}

Determine whether rollback is necessary.

Rules:
1. Check deployment health and rollout status.
2. Check the number of available rollout revisions.
3. If only one revision exists, state that rollback is unavailable.
4. If the deployment is healthy, do not recommend rollback.
5. If rollback is justified and a previous revision exists,
   suggest the appropriate kubectl rollback command.
6. Never invent revision numbers.
7. Never execute commands.
8. Explain your decision concisely.

Return:
- Deployment health
- Rollback decision
- Evidence
- Suggested command, only if justified
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "num_predict": 250,
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
        print("AI ROLLBACK ASSISTANT")
        print("=" * 45)

        print("\nCollecting Kubernetes deployment information...")

        data = collect_cluster_data()

        print("\nAnalysing deployment and rollout history with AI...\n")

        analysis = analyze_rollback(data)

        print("AI ROLLBACK ANALYSIS")
        print("=" * 45)
        print(analysis)

        print("\nNOTE: No rollback command was executed.")

    except Exception as error:
        print(f"Error: {error}")