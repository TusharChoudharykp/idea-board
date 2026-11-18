# Idea Board

A full-stack idea-sharing application built for the Halcer DevOps case study. It demonstrates a React frontend, FastAPI backend, PostgreSQL persistence, Docker Compose, Kubernetes, Terraform configurations for AWS and Google Cloud, GitHub Actions CI, and local AI-assisted DevOps workflows.

> **Deployment status:** Local Docker Compose and local Kubernetes deployments have been tested. AWS and GCP Terraform configurations are prepared but have not yet been deployed. Public cloud URLs will be added after successful deployment and verification.

## Architecture

```text
Users
  |
  v
React + TypeScript (Nginx frontend)
  |
  | /api/*
  v
FastAPI backend
  |
  v
PostgreSQL

Local: Docker Compose (frontend, backend, database)
Kubernetes: frontend/backend Deployments and Services,
            PostgreSQL Deployment and persistent volume claim
AWS target: EKS + Amazon RDS for PostgreSQL
GCP target: GKE + Cloud SQL for PostgreSQL

DevOps: GitHub Actions CI + local Ollama/Qwen assistants
```

The frontend sends API requests through the Nginx reverse proxy. FastAPI reads and writes ideas in PostgreSQL.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Web server | Nginx |
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL |
| Containers | Docker |
| Local orchestration | Docker Compose |
| Container orchestration | Kubernetes |
| AWS infrastructure | Terraform, Amazon EKS, Amazon RDS |
| Google Cloud infrastructure | Terraform, GKE, Cloud SQL |
| CI | GitHub Actions |
| Local AI | Ollama, Qwen 3.5 4B |

## Application and API

The application displays ideas, accepts new ideas, and persists them in PostgreSQL. The backend creates the required table at startup.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/ideas` | Returns ideas as a JSON array |
| POST | `/api/ideas` | Creates an idea |
| GET | `/health` | Basic backend health endpoint |

Example POST body:

```json
{
  "content": "My new idea"
}
```

The `ideas` table contains `id` (primary key), `content`, and `created_at` (timestamp).

## Run locally with Docker Compose

### Prerequisites

- Git
- Docker Desktop (or Docker Engine with the Compose plugin)

### 1. Clone the repository

```bash
git clone https://github.com/TusharChoudharykp/idea-board.git
cd idea-board
```

### 2. Create the environment file

PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Check `.env` and set local database credentials and the database URL to match the Compose configuration. Do not commit the populated `.env` file.

### 3. Build and start

```bash
docker compose up --build -d
```

### 4. Open the application

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health

### 5. Logs and shutdown

```bash
docker compose logs -f
docker compose down
```

To also delete the local PostgreSQL data volume and saved ideas:

```bash
docker compose down -v
```

## Kubernetes deployment

The `kubernetes/` directory contains namespace, frontend, backend, PostgreSQL, persistent volume claim, and local Secret manifests. These manifests have been tested against local Docker Desktop Kubernetes. They use local image names and ClusterIP Services; they are not by themselves a public cloud deployment configuration.

With a Kubernetes context selected and the images available to the cluster:

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/postgres.yaml
kubectl apply -f kubernetes/backend.yaml
kubectl apply -f kubernetes/frontend.yaml
kubectl get pods -n idea-board
kubectl get services -n idea-board
```

Create the Secret locally with the required database password before applying it. Never commit real credentials.

For local frontend access:

```bash
kubectl port-forward -n idea-board service/frontend 8080:80
```

Open http://localhost:8080 while the port-forward command is running.

For cloud deployment, publish images to a registry accessible by the cluster, update Kubernetes image references, configure a public frontend entry point, and connect the backend to the cloud provider's managed PostgreSQL service. The in-cluster PostgreSQL manifest is for local Kubernetes testing, not a replacement for managed cloud PostgreSQL.

## Infrastructure as Code (Terraform)

Provider-specific Terraform configurations are kept separate:

- `terraform/aws/`: VPC, public subnets, EKS cluster and managed node group, database security group, and Amazon RDS for PostgreSQL.
- `terraform/gcp/`: VPC network and subnets, GKE cluster and node pool, Cloud SQL for PostgreSQL.

Each provider folder contains `versions.tf`, `provider.tf`, `variables.tf`, `main.tf`, and `outputs.tf`.

### AWS plan and validation

Prerequisites: Terraform CLI, AWS CLI, and configured AWS credentials with permissions for the resources.

```powershell
aws sts get-caller-identity
cd terraform/aws
terraform init
terraform fmt -check
terraform validate
terraform plan
```

The current default region is `ap-south-1`; it can be changed through the `aws_region` variable.

### Google Cloud plan and validation

Prerequisites: Terraform CLI, Google Cloud CLI, an active project, and credentials configured for Terraform.

```powershell
gcloud auth list
gcloud config get-value project
gcloud auth application-default login
cd terraform/gcp
terraform init
terraform fmt -check
terraform validate
terraform plan -var="gcp_project_id=YOUR_GCP_PROJECT_ID"
```

The current default region is `asia-south1`.

### Deployment and cost warning

These are starting-point infrastructure definitions. They have not yet been applied or verified in live AWS/GCP accounts. A successful `terraform validate` does not guarantee that quotas, IAM permissions, provider APIs, network settings, or resource availability will permit deployment. Review every plan and current cloud pricing before applying. Cloud resources can incur charges.

## AI-assisted DevOps

The project uses a locally running Ollama model (`qwen3.5:4b`). Scripts collect logs, Kubernetes status, Terraform configuration, or GitHub Actions artifacts and ask the model for recommendations.

| Assistant | Purpose |
|---|---|
| Log analyzer | Summarizes application/Kubernetes log errors and suggests troubleshooting |
| Deployment assistant | Generates Kubernetes commands for human review |
| Configuration assistant | Reviews Kubernetes Deployment configuration and proposes improvements |
| Rollback assistant | Reviews rollout status/history and advises whether rollback is justified |
| Health and metrics assistant | Reviews pod/deployment status and available CPU/memory metrics |
| Terraform assistant | Reads AWS/GCP Terraform files and proposes infrastructure changes |
| CI assistant | Fetches a completed GitHub Actions run and log artifacts for AI analysis |

### Prerequisites and execution

Install Python, Ollama, and the `qwen3.5:4b` model. Install/configure the relevant CLI tools (`kubectl`, `terraform`, and GitHub CLI `gh`) for the assistants you use.

Start Ollama in one terminal:

```powershell
ollama run qwen3.5:4b
```

Run assistants from the repository root in another terminal:

```powershell
python ai/log_analyzer.py ai/sample.log
python ai/deployment_assistant.py
python ai/config_assistant.py
python ai/rollback_assistant.py
python ai/health_metrics_assistant.py
python ai/terraform_assistant.py
python ai/ci_ai_assistant.py
```

Each script requires its corresponding file in `ai/`. The CI assistant uses GitHub CLI authentication to fetch a completed workflow run and download its log artifacts, then sends those logs to the local Ollama endpoint.

**Human oversight and limitations:** AI output is advisory. Review generated commands, YAML, and Terraform before using them. The assistants do not automatically apply configuration, deploy infrastructure, or execute rollbacks. CPU/memory analysis depends on the Kubernetes Metrics API being available. GitHub Actions currently runs deterministic backend/frontend checks; the local CI assistant analyses uploaded artifacts after the workflow completes. Qwen is not running inside the GitHub-hosted runner, and this is not an automatic AI-triggered deployment pipeline.

## CI pipeline

Workflow: `.github/workflows/ci.yaml`. It runs on pushes and pull requests targeting `main`.

1. **Backend validation:** sets up Python 3.12, installs backend requirements, and runs Python bytecode compilation as a syntax check.
2. **Frontend build:** sets up Node.js 20, installs frontend dependencies, and runs the Vite production build.
3. **Log artifacts:** uploads backend and frontend logs for inspection and subsequent AI-assisted analysis.

See the repository's GitHub Actions tab for workflow runs.

## Cloud-agnostic design

- The same React frontend and FastAPI backend are containerized with Docker.
- PostgreSQL is the relational database on both providers.
- Kubernetes is the orchestration interface on both providers.
- Terraform manages provider-specific infrastructure in separate AWS and GCP directories.
- Provider-specific resources (EKS/RDS versus GKE/Cloud SQL) are isolated from application code.

The design is **cloud-portable, not provider-identical**. AWS and GCP still require provider-specific Terraform resources, credentials, cluster access, database endpoints, and image-registry setup. The application containers and core API remain the same across providers.

## Repository structure

```text
idea-board/
├── .github/workflows/ci.yaml
├── ai/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── kubernetes/
│   ├── namespace.yaml
│   ├── postgres.yaml
│   ├── backend.yaml
│   ├── frontend.yaml
│   └── secret.yaml       # local only; ignored by Git
├── terraform/
│   ├── aws/
│   └── gcp/
├── .env.example
├── docker-compose.yml
└── README.md
```

## Security and cost notes

- Keep `.env`, real Kubernetes Secrets, cloud service-account keys, and Terraform state files out of Git.
- Use least-privilege IAM permissions for cloud deployments.
- Avoid publicly exposing managed PostgreSQL unless there is a specific secured requirement.
- Review Terraform plans and cloud pricing before creating resources.
- Remove temporary cloud resources when no longer needed, after confirming that required data will not be lost.

## Deployment status and URLs

| Target | Infrastructure status | Application URL |
|---|---|---|
| Local Docker Compose | Tested | http://localhost:8080 |
| Local Kubernetes | Tested with port forwarding | http://localhost:8080 (while port-forward is running) |
| AWS | Terraform prepared; cloud deployment pending | To be added after deployment |
| Google Cloud | Terraform prepared; cloud deployment pending | To be added after deployment |

Cloud URLs will be published here only after both deployments are completed and verified.