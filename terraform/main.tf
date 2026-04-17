terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.25.0"
    }
  }
}

provider "google" {
  # Configuration options
}

resource "google_bigquery_dataset" "dataset" {
  project                    = var.project
  dataset_id                 = var.dataset
  friendly_name              = "eia"
  location                   = var.project_location
  delete_contents_on_destroy = true
}