variable "project_id" {
  description = "El ID del proyecto de Google Cloud Platform"
  type        = string
}

variable "region" {
  description = "Región principal para desplegar los recursos (US para aprovechar Free Tier)"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Ambiente de despliegue (dev, prod)"
  type        = string
  default     = "dev"
}
