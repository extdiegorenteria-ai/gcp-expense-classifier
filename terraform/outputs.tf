output "raw_bucket_name" {
  description = "Nombre del bucket de Cloud Storage donde se deben subir los comprobantes"
  value       = google_storage_bucket.raw_receipts_bucket.name
}

output "bigquery_table_id" {
  description = "Identificador completo de la tabla de BigQuery para Looker Studio"
  value       = "${google_bigquery_table.expenses_table.dataset_id}.${google_bigquery_table.expenses_table.table_id}"
}

output "cloud_function_uri" {
  description = "URI del servicio subyacente de la Cloud Function"
  value       = google_cloudfunctions2_function.expense_classifier_fn.service_config[0].uri
}

output "service_account_email" {
  description = "Email de la Service Account asignada a la Cloud Function"
  value       = google_service_account.function_sa.email
}
