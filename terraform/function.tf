# ---------------------------------------------------------------------------------------------------------------------
# CÓMPUTO SERVERLESS (CLOUD FUNCTIONS 2ND GEN + EVENTARC)
# ---------------------------------------------------------------------------------------------------------------------
resource "google_cloudfunctions2_function" "expense_classifier_fn" {
  name        = "fn-clasificador-gastos"
  location    = var.region
  description = "Función reactiva que extrae datos con Vertex AI y los almacena en BigQuery"

  build_config {
    runtime     = "python311"
    entry_point = "procesar_comprobante"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_bucket.name
        object = google_storage_bucket_object.function_code.name
      }
    }
  }

  service_config {
    max_instance_count    = 5
    min_instance_count    = 0
    available_memory      = "512Mi"
    timeout_seconds       = 120
    service_account_email = google_service_account.function_sa.email
    environment_variables = {
      GCP_PROJECT_ID   = var.project_id
      BIGQUERY_DATASET = google_bigquery_dataset.expenses_dataset.dataset_id
      BIGQUERY_TABLE   = google_bigquery_table.expenses_table.table_id
      VERTEX_LOCATION  = var.region
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    retry_policy   = "RETRY_POLICY_RETRY"
    event_filters {
      attribute = "bucket"
      value     = google_storage_bucket.raw_receipts_bucket.name
    }
  }

  depends_on = [
    google_project_service.gcp_services,
    google_storage_bucket_iam_member.storage_viewer,
    google_project_iam_member.bigquery_editor,
    google_project_iam_member.vertex_ai_user,
    google_project_iam_member.eventarc_service_agent,
    google_project_iam_member.gcs_pubsub_publisher
  ]
}
