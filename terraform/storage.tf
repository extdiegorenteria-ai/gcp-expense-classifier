# ---------------------------------------------------------------------------------------------------------------------
# CAPA DE ALMACENAMIENTO (CLOUD STORAGE)
# ---------------------------------------------------------------------------------------------------------------------

# Bucket para ingesta de comprobantes crudos (facturas, boletas, tickets)
resource "google_storage_bucket" "raw_receipts_bucket" {
  name                        = "${var.project_id}-gastos-raw"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  depends_on = [google_project_service.gcp_services]
}

# Bucket para almacenar el empaquetado del código de la Cloud Function
resource "google_storage_bucket" "function_source_bucket" {
  name                        = "${var.project_id}-function-source"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  depends_on = [google_project_service.gcp_services]
}

# Empaquetado del código de src/
data "archive_file" "function_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/function-source.zip"
}

resource "google_storage_bucket_object" "function_code" {
  name   = "function-source-${data.archive_file.function_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_source_bucket.name
  source = data.archive_file.function_zip.output_path
}
