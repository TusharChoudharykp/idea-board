variable "project_name" {
  description = "Name of the application"
  type        = string
  default     = "idea-board"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "Cloud deployment region"
  type        = string
}