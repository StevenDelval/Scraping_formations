# Simplon Training Comparison Database

## Purpose

The goal of this project is to create a comprehensive database that enables Simplon to compare its training offerings with those of other training centers. This will help employees understand which trainings face strong competition and provide potential learners with alternatives if Simplon's courses are fully booked.

## Project Overview

This project includes:

- **Scraping**: Automated data scraping to gather information about training offerings from various centers.
- **Database Setup**: Instructions for building a PostgreSQL database on Azure, including data import procedures
- **API Development**: Creation of a FastAPI-based API with token-based authentication and Ml-ops monitoring.


## Dependencies

- Azure
- PostgreSQL

## Setup Instructions

### Initialize and Apply Terraform Configuration

```bash
cd terraform
terraform init -upgrade
terraform plan -var-file="terraform.tfvars" -out main.tfplan
terraform apply -var-file="terraform.tfvars" -auto-approve
```

### Destroy Terraform Configuration
```bash
terraform plan -destroy -out main.destroy.tfplan
terraform apply main.destroy.tfplan
```
