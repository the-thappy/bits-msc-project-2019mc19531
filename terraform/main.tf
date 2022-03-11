# INSTALL REQUIRED PROVIDERS.

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.60.0"
    }
  }
}

provider "google" {
  # Configuration options
}

provider "google-beta" {
  # Configuration options
}

# The GCS bucket to receive data from AE
resource "google_storage_bucket" "data-bucket" {
  name                        = "${var.env}-data-bucket"
  project                     = var.project-id
  force_destroy               = true
  location                    = "US"
  storage_class               = "MULTI_REGIONAL"
  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "thappy"
  location   = "US"
}
