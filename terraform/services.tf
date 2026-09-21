# ---------------------------------------------------------------------------------------------------------------------
# HABILITACIÓN DE SERVICIOS Y APIS EN GCP
# ---------------------------------------------------------------------------------------------------------------------
locals {
  services = [
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "eventarc.googleapis.com",
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "logging.googleapis.com"
  ]
}

resource "google_project_service" "gcp_services" {
  for_each           = toset(local.services)
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
