import os
import json
import uuid
import logging
from datetime import datetime, timezone
import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import storage
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Configuración de Logging Estructurado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("expense-classifier")

# Variables de entorno inyectadas por Terraform
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "gastos")
BIGQUERY_TABLE = os.environ.get("BIGQUERY_TABLE", "gastos_clasificados")
VERTEX_LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")

# Inicialización de clientes (fuera del handler para reutilización en warm starts)
storage_client = storage.Client(project=PROJECT_ID)
bq_client = bigquery.Client(project=PROJECT_ID)
vertexai.init(project=PROJECT_ID, location=VERTEX_LOCATION)

# Definición del esquema JSON estricto para Gemini 1.5 Flash
EXTRACTION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "fecha_gasto": {
            "type": "STRING",
            "description": "Fecha de la transacción en formato YYYY-MM-DD. Si no se visualiza el año, asumir el año corriente."
        },
        "comercio": {
            "type": "STRING",
            "description": "Nombre de la tienda, comercio o razón social del emisor del comprobante."
        },
        "categoria": {
            "type": "STRING",
            "enum": [
                "Alimentacion",
                "Transporte",
                "Servicios",
                "Salud",
                "Educacion",
                "Ocio",
                "Hogar",
                "Otros"
            ],
            "description": "Categoría estandarizada en la que clasifica el gasto."
        },
        "moneda": {
            "type": "STRING",
            "description": "Código de moneda ISO 4217 de 3 letras (ej. PEN, USD, EUR, MXN, COP)."
        },
        "monto_total": {
            "type": "NUMBER",
            "description": "Importe total final a pagar en el comprobante."
        },
        "monto_impuesto": {
            "type": "NUMBER",
            "description": "Importe de impuestos desglosados (IGV, IVA, Tax). Si no existe desglose, 0.0."
        },
        "confianza_extraccion": {
            "type": "NUMBER",
            "description": "Estimación de confianza de la lectura de 0.0 a 1.0 según la nitidez del documento."
        }
    },
    "required": [
        "fecha_gasto",
        "comercio",
        "categoria",
        "moneda",
        "monto_total",
        "confianza_extraccion"
    ]
}


@functions_framework.cloud_event
def procesar_comprobante(cloud_event: CloudEvent) -> None:
    """Manejador del evento de Cloud Storage disparado por Eventarc."""
    data = cloud_event.data
    bucket_name = data.get("bucket")
    file_name = data.get("name")
    content_type = data.get("contentType", "application/pdf")

    logger.info(f"Nuevo archivo detectado: gs://{bucket_name}/{file_name} (tipo: {content_type})")

    # Filtro para ignorar directorios o archivos ocultos
    if file_name.endswith("/") or file_name.startswith("."):
        logger.info("El objeto es un prefijo de directorio o archivo oculto. Omitiendo.")
        return

    gcs_uri = f"gs://{bucket_name}/{file_name}"

    try:
        # 1. Cargar el modelo multimodal Gemini 2.5 Flash con Structured Outputs
        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=[
                "Eres un auditor y contador experto. Tu tarea es analizar comprobantes de pago,",
                "facturas, boletas y tickets (en imagen o PDF) para extraer con total precisión los datos",
                "financieros y clasificarlos en las categorías requeridas.",
                "Devuelve ÚNICAMENTE los campos solicitados en el esquema estructurado."
            ]
        )

        # 2. Pasar el archivo directamente mediante su URI de Cloud Storage
        doc_part = Part.from_uri(uri=gcs_uri, mime_type=content_type)

        prompt = "Analiza el comprobante adjunto y extrae los datos clave clasificados en formato estructurado."

        response = model.generate_content(
            [doc_part, prompt],
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": EXTRACTION_SCHEMA,
                "temperature": 0.1,
            }
        )

        extracted_data = json.loads(response.text)
        logger.info(f"Extracción exitosa: {extracted_data}")

        # 3. Preparar el registro para BigQuery
        table_ref = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
        transaction_id = str(uuid.uuid4())
        processing_timestamp = datetime.now(timezone.utc).isoformat()

        row_to_insert = {
            "id_transaccion": transaction_id,
            "fecha_gasto": extracted_data.get("fecha_gasto"),
            "comercio": extracted_data.get("comercio"),
            "categoria": extracted_data.get("categoria"),
            "moneda": extracted_data.get("moneda"),
            "monto_total": float(extracted_data.get("monto_total", 0.0)),
            "monto_impuesto": float(extracted_data.get("monto_impuesto", 0.0)) if extracted_data.get("monto_impuesto") is not None else 0.0,
            "archivo_origen_gcs": gcs_uri,
            "confianza_extraccion": float(extracted_data.get("confianza_extraccion", 1.0)),
            "fecha_procesamiento": processing_timestamp
        }

        # 4. Inserción streaming en BigQuery
        errors = bq_client.insert_rows_json(table_ref, [row_to_insert])

        if errors:
            logger.error(f"Error al insertar en BigQuery: {errors}")
            raise RuntimeError(f"Falla en BigQuery insert_rows_json: {errors}")

        logger.info(f"Transacción {transaction_id} guardada con éxito en BigQuery ({table_ref}).")

    except Exception as e:
        logger.error(f"Error procesando el comprobante {gcs_uri}: {str(e)}", exc_info=True)
        raise e
