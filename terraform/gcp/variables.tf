variable "project_name" {
  description = "Application name"
  type        = string
  default     = "idea-board"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "gcp_project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "gcp_region" {
  description = "Google Cloud deployment region"
  type        = string
  default     = "asia-south1"
}