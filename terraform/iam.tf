# ---------------------------------------------------------------------------------------------------------------------
# SEGURIDAD Y PERMISOS (CLOUD IAM - LEAST PRIVILEGE)
# ---------------------------------------------------------------------------------------------------------------------
resource "google_service_account" "function_sa" {
  account_id   = "sa-expense-processor"
  display_name = "Service Account para procesamiento de gastos con IA"
}

# Permiso para invocar modelos en Vertex AI
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

# Permiso para insertar datos en BigQuery
resource "google_project_iam_member" "bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

# Permiso para leer los archivos que caen en el bucket
resource "google_storage_bucket_iam_member" "storage_viewer" {
  bucket = google_storage_bucket.raw_receipts_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.function_sa.email}"
}

# Service Agent de Eventarc y GCS para disparar triggers
data "google_project" "current_project" {
  project_id = var.project_id
}

data "google_storage_project_service_account" "gcs_account" {
  project    = var.project_id
  depends_on = [google_project_service.gcp_services]
}

resource "google_project_iam_member" "gcs_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
}

resource "google_project_iam_member" "eventarc_service_agent" {
  project = var.project_id
  role    = "roles/eventarc.serviceAgent"
  member  = "serviceAccount:service-${data.google_project.current_project.number}@gcp-sa-eventarc.iam.gserviceaccount.com"
}
