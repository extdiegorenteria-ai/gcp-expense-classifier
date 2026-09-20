import os
import subprocess
import sys

HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Proyecto Final GCP - Pipeline Clasificador de Gastos</title>
  <style>
    @page {
      size: A4;
      margin: 20mm;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #202124;
      line-height: 1.6;
      margin: 0;
      padding: 0;
      font-size: 11pt;
    }
    .header {
      border-bottom: 3px solid #1a73e8;
      padding-bottom: 15px;
      margin-bottom: 25px;
    }
    h1 {
      color: #1a73e8;
      margin: 0 0 8px 0;
      font-size: 22pt;
    }
    .badge {
      display: inline-block;
      background-color: #e8f0fe;
      color: #1a73e8;
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 9pt;
      font-weight: 600;
    }
    .meta-box {
      background-color: #f8f9fa;
      border-left: 4px solid #1a73e8;
      padding: 12px 16px;
      margin: 20px 0;
      font-size: 10pt;
    }
    h2 {
      color: #202124;
      border-bottom: 1px solid #dadce0;
      padding-bottom: 6px;
      margin-top: 28px;
      font-size: 14pt;
    }
    h3 {
      color: #3c4043;
      margin-top: 18px;
      font-size: 12pt;
    }
    p, li {
      color: #3c4043;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 18px 0;
      font-size: 9.5pt;
    }
    th, td {
      border: 1px solid #dadce0;
      padding: 8px 12px;
      text-align: left;
    }
    th {
      background-color: #f1f3f4;
      color: #202124;
      font-weight: 600;
    }
    .diagram-container {
      background-color: #f8f9fa;
      border: 1px solid #dadce0;
      border-radius: 8px;
      padding: 20px;
      margin: 20px 0;
      text-align: center;
    }
    .diagram-svg {
      width: 100%;
      max-width: 650px;
      height: auto;
    }
    .step-card {
      margin-bottom: 14px;
    }
    .step-number {
      font-weight: 700;
      color: #1a73e8;
    }
    code {
      background-color: #f1f3f4;
      padding: 2px 5px;
      border-radius: 4px;
      font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 9pt;
    }
    .page-break {
      page-break-before: always;
    }
    .footer {
      margin-top: 30px;
      font-size: 8.5pt;
      color: #70757a;
      text-align: center;
      border-top: 1px solid #dadce0;
      padding-top: 10px;
    }
  </style>
</head>
<body>

  <div class="header">
    <span class="badge">PROYECTO FINAL - GOOGLE CLOUD PLATFORM</span>
    <h1>Pipeline Inteligente de Clasificación de Gastos</h1>
    <p style="margin: 0; color: #5f6368;">Solución Serverless y Event-Driven con Visión Artificial y Analítica Columnar</p>
  </div>

  <div class="meta-box">
    <strong>Repositorio GitHub con código e IaC:</strong> 
    <a href="https://github.com/tu-usuario/gcp-expense-classifier" style="color: #1a73e8; text-decoration: none;">https://github.com/tu-usuario/gcp-expense-classifier</a><br>
    <strong>Arquitectura:</strong> 100% Serverless en GCP (Storage, Cloud Functions, Vertex AI, BigQuery, Looker Studio)
  </div>

  <h2>1. Identificación del Proceso a Automatizar</h2>
  <p>
    El control de gastos personales y la rendición de cuentas de negocios suele depender de la revisión manual de tickets, boletas y facturas físicas o digitales. Este proceso manual adolece de fricciones recurrentes: pérdida de comprobantes, errores humanos de transcripción en hojas de cálculo y demoras de semanas para conocer el estado financiero real.
  </p>
  <p>
    <strong>Objetivo de la solución:</strong> Implementar un pipeline desatendido donde el usuario únicamente sube fotos o documentos PDF de comprobantes a un bucket de almacenamiento. Automáticamente, mediante modelos de Inteligencia Artificial multimodal en la nube, se extraen los campos clave estructurados (comercio, fecha, categoría, montos e impuestos) y se persisten en un almacén analítico para visualización en tiempo real.
  </p>

  <h2>2. Diagrama de Arquitectura de la Solución</h2>
  <div class="diagram-container">
    <svg class="diagram-svg" viewBox="0 0 780 180" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1a73e8"/>
        </marker>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.1"/>
        </filter>
      </defs>

      <!-- Nodo 1: Cloud Storage -->
      <g filter="url(#shadow)">
        <rect x="20" y="45" width="130" height="90" rx="8" fill="#ffffff" stroke="#4285f4" stroke-width="2"/>
        <text x="85" y="75" text-anchor="middle" font-size="11" font-weight="700" fill="#1a73e8">1. INGESTA</text>
        <text x="85" y="95" text-anchor="middle" font-size="10" font-weight="600" fill="#202124">Cloud Storage</text>
        <text x="85" y="112" text-anchor="middle" font-size="8.5" fill="#5f6368">Bucket Raw (PDF/Img)</text>
      </g>

      <!-- Flecha 1 -->
      <line x1="150" y1="90" x2="185" y2="90" stroke="#1a73e8" stroke-width="2" marker-end="url(#arrow)"/>
      <text x="168" y="82" text-anchor="middle" font-size="7.5" fill="#5f6368">Finalized</text>

      <!-- Nodo 2: Cloud Functions -->
      <g filter="url(#shadow)">
        <rect x="190" y="45" width="135" height="90" rx="8" fill="#ffffff" stroke="#4285f4" stroke-width="2"/>
        <text x="257" y="75" text-anchor="middle" font-size="11" font-weight="700" fill="#1a73e8">2. CÓMPUTO</text>
        <text x="257" y="95" text-anchor="middle" font-size="10" font-weight="600" fill="#202124">Cloud Functions v2</text>
        <text x="257" y="112" text-anchor="middle" font-size="8.5" fill="#5f6368">Eventarc / Python</text>
      </g>

      <!-- Flecha bidireccional a Vertex -->
      <line x1="325" y1="90" x2="360" y2="90" stroke="#1a73e8" stroke-width="2" marker-end="url(#arrow)"/>

      <!-- Nodo 3: Vertex AI -->
      <g filter="url(#shadow)">
        <rect x="365" y="45" width="130" height="90" rx="8" fill="#ffffff" stroke="#34a853" stroke-width="2"/>
        <text x="430" y="75" text-anchor="middle" font-size="11" font-weight="700" fill="#1e8e3e">3. INTELIGENCIA</text>
        <text x="430" y="95" text-anchor="middle" font-size="10" font-weight="600" fill="#202124">Vertex AI</text>
        <text x="430" y="112" text-anchor="middle" font-size="8.5" fill="#5f6368">Gemini 1.5 Flash</text>
      </g>

      <!-- Flecha a BigQuery -->
      <line x1="495" y1="90" x2="530" y2="90" stroke="#1a73e8" stroke-width="2" marker-end="url(#arrow)"/>
      <text x="512" y="82" text-anchor="middle" font-size="7.5" fill="#5f6368">JSON Stream</text>

      <!-- Nodo 4: BigQuery -->
      <g filter="url(#shadow)">
        <rect x="535" y="45" width="125" height="90" rx="8" fill="#ffffff" stroke="#fbbc04" stroke-width="2"/>
        <text x="597" y="75" text-anchor="middle" font-size="11" font-weight="700" fill="#b06000">4. ALMACÉN</text>
        <text x="597" y="95" text-anchor="middle" font-size="10" font-weight="600" fill="#202124">BigQuery</text>
        <text x="597" y="112" text-anchor="middle" font-size="8.5" fill="#5f6368">Partición diaria</text>
      </g>

      <!-- Flecha a Looker -->
      <line x1="660" y1="90" x2="685" y2="90" stroke="#1a73e8" stroke-width="2" marker-end="url(#arrow)"/>

      <!-- Nodo 5: Looker Studio -->
      <g filter="url(#shadow)">
        <rect x="690" y="55" width="75" height="70" rx="8" fill="#ffffff" stroke="#ea4335" stroke-width="2"/>
        <text x="727" y="82" text-anchor="middle" font-size="9" font-weight="700" fill="#d93025">5. BI</text>
        <text x="727" y="100" text-anchor="middle" font-size="9" font-weight="600" fill="#202124">Looker</text>
      </g>
    </svg>
  </div>

  <h2>3. Servicios de Google Cloud Utilizados</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Servicio de GCP</th>
        <th style="width: 30%;">Capa de la Arquitectura</th>
        <th>Rol y Justificación Técnica</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Cloud Storage (GCS)</strong></td>
        <td>Ingesta (*Landing Zone*)</td>
        <td>Almacenamiento de objetos seguro y duradero para los recibos crudos. Emite eventos a nivel de objeto para activar el flujo.</td>
      </tr>
      <tr>
        <td><strong>Cloud Functions (2nd Gen)</strong></td>
        <td>Cómputo Serverless</td>
        <td>Ejecución de lógica basada en microcontenedores sobre Cloud Run. Escala a cero, reduciendo costos a cero en reposo.</td>
      </tr>
      <tr>
        <td><strong>Vertex AI (Gemini 1.5 Flash)</strong></td>
        <td>Inferencia Multimodal</td>
        <td>Extracción precisa de datos textuales y numéricos desde imágenes o PDFs, asegurando esquema estricto (JSON Schema).</td>
      </tr>
      <tr>
        <td><strong>BigQuery</strong></td>
        <td>Data Warehouse Analítico</td>
        <td>Base de datos analítica columnar. Se particiona por fecha de transacción para optimizar tiempos de consulta y minimizar costos.</td>
      </tr>
      <tr>
        <td><strong>Looker Studio</strong></td>
        <td>Visualización / BI</td>
        <td>Dashboards dinámicos interactivos para control presupuestal, desglose por categorías y tendencias de gasto.</td>
      </tr>
      <tr>
        <td><strong>Cloud IAM</strong></td>
        <td>Seguridad y Gobierno</td>
        <td>Service Account con privilegios mínimos (BigQuery Data Editor, Vertex AI User, Storage Object Viewer).</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <h2>4. Descripción Paso a Paso de la Solución</h2>

  <div class="step-card">
    <p><span class="step-number">Paso 1: Carga de Comprobante en Cloud Storage</span><br>
    El usuario sube el archivo (imagen JPG/PNG o documento PDF) al bucket <code>gs://[PROJECT_ID]-gastos-raw/inbox/</code>. El bucket cuenta con reglas de ciclo de vida para optimizar costos de almacenamiento a largo plazo.</p>
  </div>

  <div class="step-card">
    <p><span class="step-number">Paso 2: Disparo de Evento mediante Eventarc</span><br>
    La finalización de la carga dispara una notificación <code>google.cloud.storage.object.v1.finalized</code>. Eventarc enruta este evento de inmediato a la Cloud Function de 2da generación.</p>
  </div>

  <div class="step-card">
    <p><span class="step-number">Paso 3: Extracción Inteligente con Vertex AI</span><br>
    La Cloud Function toma la referencia URI del archivo y realiza una consulta multimodal a <code>gemini-1.5-flash</code> con <em>Structured Outputs</em> activado. El modelo extrae con rigor la fecha, el comercio emisor, la categoría presupuestal, la moneda, el importe total y los impuestos.</p>
  </div>

  <div class="step-card">
    <p><span class="step-number">Paso 4: Inserción Streaming en BigQuery</span><br>
    La función valida el JSON estructurado, genera un identificador único (UUID) y realiza un <em>streaming insert</em> directo en la tabla <code>gastos.gastos_clasificados</code>, asociando además la URI de auditoría del archivo original.</p>
  </div>

  <div class="step-card">
    <p><span class="step-number">Paso 5: Visualización y Toma de Decisiones en Looker Studio</span><br>
    A través del conector nativo de BigQuery, Looker Studio presenta un reporte financiero en tiempo real que clasifica gastos por categorías, compara contra presupuestos mensuales y detecta picos inusuales de gasto.</p>
  </div>

  <h2>5. Infraestructura como Código (Terraform)</h2>
  <p>
    Toda la solución se encuentra completamente codificada bajo Terraform en el repositorio, garantizando el despliegue automatizado y la reproducibilidad de la infraestructura en cualquier proyecto de Google Cloud:
  </p>
  <ul>
    <li><code>terraform/main.tf</code>: Aprovisionamiento de buckets GCS, tabla particionada de BigQuery, Service Account con IAM mínimo y Cloud Function v2.</li>
    <li><code>terraform/variables.tf</code> y <code>outputs.tf</code>: Parametrización y exportación de endpoints y nombres de recursos.</li>
    <li><code>src/main.py</code>: Código Python 3.11 con SDKs oficiales de Google Cloud y Vertex AI.</li>
  </ul>

  <h2>6. Cumplimiento del Free Tier y Costos</h2>
  <p>
    La arquitectura fue concebida para no incurrir en gastos fijos. Al ser 100% serverless, no consume recursos en reposo:
  </p>
  <ul>
    <li><strong>Almacenamiento:</strong> Dentro de los 5 GB mensuales del Free Tier de Cloud Storage.</li>
    <li><strong>Cómputo:</strong> Las primeras 2 millones de ejecuciones mensuales de Cloud Functions son gratuitas.</li>
    <li><strong>Consultas:</strong> BigQuery incluye 10 GB de almacenamiento y 1 TB de procesamiento de consultas gratuito mensual.</li>
    <li><strong>Inferencia:</strong> Gemini 1.5 Flash en Vertex AI tiene un coste inferior a $0.05 USD por cada 500 comprobantes procesados, cubierto por los créditos iniciales de Google Cloud.</li>
  </ul>

  <div class="footer">
    Proyecto Final de Google Cloud Platform • Entregable Académico y Profesional
  </div>

</body>
</html>
"""

def generate_pdf():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(base_dir, "docs", "entrega_proyecto_gcp.html")
    pdf_path = os.path.join(base_dir, "Proyecto_Final_GCP_Clasificador_Gastos.pdf")
    
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"HTML generado en: {html_path}")

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    
    print("Compilando PDF con Google Chrome...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"PDF generado exitosamente en: {pdf_path}")
    else:
        print(f"Error generando PDF: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

if __name__ == "__main__":
    generate_pdf()
