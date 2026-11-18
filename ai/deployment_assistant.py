import json
import subprocess
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3.5:4b"
NAMESPACE = "idea-board"


def get_kubernetes_info():
    deployments = subprocess.run(
        ["kubectl", "get", "deployments", "-n", NAMESPACE, "-o", "wide"],
        capture_output=True, text=True
    )

    services = subprocess.run(
        ["kubectl", "get", "services", "-n", NAMESPACE],
        capture_output=True, text=True
    )

    if deployments.returncode != 0 or services.returncode != 0:
        raise RuntimeError(deployments.stderr + services.stderr)

    return f"""
DEPLOYMENTS:
{deployments.stdout}

SERVICES:
{services.stdout}
"""


def generate_commands(task, cluster_info):
    prompt = f"""
You are a Kubernetes DevOps assistant.

Based on the actual Kubernetes information below,
generate the kubectl commands required for this task:

TASK:
{task}

KUBERNETES INFORMATION:
{cluster_info}

Rules:
1. Generate valid kubectl commands.
2. Use namespace idea-board.
3. Never use kubectl delete.
4. Never delete or recreate deployments.
5. Never use force deletion.
6. For restarting a deployment, use:
   kubectl rollout restart deployment/<name> -n idea-board
7. For checking deployment status, use:
   kubectl rollout status deployment/<name> -n idea-board
8. Never execute commands.
9. Explain each command.
10. If a task cannot be completed safely, explain why.

Return commands and a short explanation.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 300
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
    print("AI KUBERNETES DEPLOYMENT ASSISTANT")
    print("=" * 45)

    task = input("\nWhat deployment task do you want to perform? ")

    try:
        cluster_info = get_kubernetes_info()
        print("\nGenerating Kubernetes commands using Qwen...\n")

        result = generate_commands(task, cluster_info)

        print("AI-GENERATED COMMANDS")
        print("=" * 45)
        print(result)

        print("\nReview all commands before executing them.")

    except Exception as error:
        print(f"Error: {error}")
