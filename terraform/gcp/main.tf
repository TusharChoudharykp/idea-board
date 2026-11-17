# Create VPC network
resource "google_compute_network" "main" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
}

# Create first subnet
resource "google_compute_subnetwork" "subnet_a" {
  name          = "${var.project_name}-subnet-a"
  ip_cidr_range = "10.1.0.0/20"
  region        = var.gcp_region
  network       = google_compute_network.main.id
}

# Create second subnet
resource "google_compute_subnetwork" "subnet_b" {
  name          = "${var.project_name}-subnet-b"
  ip_cidr_range = "10.2.0.0/20"
  region        = var.gcp_region
  network       = google_compute_network.main.id
}


# Create GKE cluster
resource "google_container_cluster" "main" {
  name     = "${var.project_name}-${var.environment}"
  location = var.gcp_region

  network    = google_compute_network.main.id
  subnetwork = google_compute_subnetwork.subnet_a.id

  initial_node_count  = 1
  deletion_protection = false

  ip_allocation_policy {}
}

# Create GKE worker node pool
resource "google_container_node_pool" "main" {
  name     = "${var.project_name}-node-pool"
  location = var.gcp_region
  cluster  = google_container_cluster.main.name

  node_count = 1

  node_config {
    machine_type = "e2-small"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}


# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "postgres" {
  name             = "${var.project_name}-postgres"
  database_version = "POSTGRES_17"
  region           = var.gcp_region

  settings {
    tier              = "db-f1-micro"
    availability_type = "ZONAL"

    ip_configuration {
      ipv4_enabled = true
    }

    backup_configuration {
      enabled = false
    }
  }

  deletion_protection = false
}

# Create application database
resource "google_sql_database" "database" {
  name     = "ideaboard"
  instance = google_sql_database_instance.postgres.name
}