# ---------------------------------------------------------------------------------------------------------------------
# CAPA DE DATOS ANALÍTICOS (BIGQUERY)
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
