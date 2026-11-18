import json
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3.5:4b"

TERRAFORM_DIR = Path(__file__).resolve().parent.parent / "terraform"


def collect_terraform_files():
    infrastructure = {}

    for cloud in ["aws", "gcp"]:
        cloud_dir = TERRAFORM_DIR / cloud
        files = {}

        if not cloud_dir.exists():
            continue

        for file_path in cloud_dir.rglob("*.tf"):
            relative_path = str(file_path.relative_to(TERRAFORM_DIR))
            files[relative_path] = file_path.read_text(encoding="utf-8")

        infrastructure[cloud] = files

    return infrastructure


def generate_iac(infrastructure, task):
    prompt = f"""
You are a Terraform and cloud infrastructure engineer.

Here is the existing AWS and GCP Terraform configuration:

{json.dumps(infrastructure, indent=2)}

User request:
{task}

Requirements:
1. Analyse the existing configuration before suggesting changes.
2. Generate valid Terraform HCL where appropriate.
3. Identify the target cloud provider and file.
4. Explain the purpose of the proposed configuration.
5. Reuse existing variables and resources where appropriate.
6. Do not invent existing resource names.
7. Highlight assumptions and potential cloud costs.
8. Never include credentials, passwords or access keys.
9. Do not apply or deploy infrastructure.

Clearly separate proposed Terraform code from explanations.
"""


    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "num_predict": 500,
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
        print("AI TERRAFORM GENERATION ASSISTANT")
        print("=" * 45)

        infrastructure = collect_terraform_files()

        if not any(infrastructure.values()):
            print("No AWS or GCP Terraform files found.")
            raise SystemExit(1)

        print("\nTerraform files collected:")
        for cloud, files in infrastructure.items():
            for filename in files:
                print(f"- {filename}")

        print("\nEnter an infrastructure change to propose.")
        task = input("\nYour request: ").strip()

        if not task:
            print("No request provided.")
            raise SystemExit(1)

        print("\nGenerating Terraform proposal with AI...\n")

        proposal = generate_iac(infrastructure, task)

        print("AI GENERATED TERRAFORM PROPOSAL")
        print("=" * 45)
        print(proposal)

        print("\nNOTE: No Terraform files were modified or deployed.")

    except Exception as error:
        print(f"Error: {error}")