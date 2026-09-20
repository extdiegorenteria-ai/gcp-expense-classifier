terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------------------------------------------------
# 1. HABILITACIÓN DE SERVICIOS Y APIS EN GCP
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
  for_each           = toset(locals.services)
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# ---------------------------------------------------------------------------------------------------------------------
# 2. CAPA DE ALMACENAMIENTO (CLOUD STORAGE)
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
      type = "SetStorageClass"
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

# ---------------------------------------------------------------------------------------------------------------------
# 3. CAPA DE DATOS ANALÍTICOS (BIGQUERY)
# ---------------------------------------------------------------------------------------------------------------------
resource "google_bigquery_dataset" "expenses_dataset" {
  dataset_id                  = "gastos"
  friendly_name               = "Dataset de Gastos Clasificados"
  description                 = "Almacén analítico de comprobantes procesados con IA"
  location                    = var.region
  default_table_expiration_ms = null

  depends_on = [google_project_service.gcp_services]
}

resource "google_bigquery_table" "expenses_table" {
  dataset_id = google_bigquery_dataset.expenses_dataset.dataset_id
  table_id   = "gastos_clasificados"

  time_partitioning {
    type  = "DAY"
    field = "fecha_gasto"
  }

  clustering = ["categoria", "moneda"]

  schema = jsonencode([
    {
      name        = "id_transaccion"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Identificador único UUID de la transacción"
    },
    {
      name        = "fecha_gasto"
      type        = "DATE"
      mode        = "REQUIRED"
      description = "Fecha de emisión del comprobante"
    },
    {
      name        = "comercio"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Nombre o razón social del establecimiento"
    },
    {
      name        = "categoria"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Categoría estandarizada (Alimentacion, Transporte, etc.)"
    },
    {
      name        = "moneda"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Código de moneda ISO 4217"
    },
    {
      name        = "monto_total"
      type        = "NUMERIC"
      mode        = "REQUIRED"
      description = "Monto final facturado"
    },
    {
      name        = "monto_impuesto"
      type        = "NUMERIC"
      mode        = "NULLABLE"
      description = "Monto discriminado de impuestos (IGV/IVA)"
    },
    {
      name        = "archivo_origen_gcs"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "URI del archivo en Cloud Storage para trazabilidad"
    },
    {
      name        = "confianza_extraccion"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Nivel de confianza retornado por el modelo"
    },
    {
      name        = "fecha_procesamiento"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Momento UTC en que se procesó el documento"
    }
  ])

  depends_on = [google_bigquery_dataset.expenses_dataset]
}

# ---------------------------------------------------------------------------------------------------------------------
# 4. SEGURIDAD Y PERMISOS (CLOUD IAM - LEAST PRIVILEGE)
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

# ---------------------------------------------------------------------------------------------------------------------
# 5. CÓMPUTO SERVERLESS (CLOUD FUNCTIONS 2ND GEN + EVENTARC)
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
    max_instance_count = 5
    min_instance_count = 0
    available_memory   = "512Mi"
    timeout_seconds    = 120
    service_account_email = google_service_account.function_sa.email
    environment_variables = {
      GCP_PROJECT_ID     = var.project_id
      BIGQUERY_DATASET   = google_bigquery_dataset.expenses_dataset.dataset_id
      BIGQUERY_TABLE     = google_bigquery_table.expenses_table.table_id
      VERTEX_LOCATION    = var.region
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
    google_project_iam_member.vertex_ai_user
  ]
}
