# 🛠️ Installation & Setup Guide

This document describes how to deploy the development and production environment for the ERP Report Generator.

## 1. Prerequisites
To run this project, you must have the following installed on your machine:
* **Docker Desktop** (for Windows/Mac) or **Docker Engine** (for Linux).
* **Docker Compose V2** (included with Docker Desktop).
* At least **15GB of free disk space** (to accommodate the 16M rows database volume).

##2. Project Directory Overview

The project is organized to separate data, logic, and infrastructure. Below is the complete structure:

* **data/**: Source files (CSV/Excel). Place the sales data here.
* **sql/**: Contains `DB.sql`, the main schema for the MySQL database.
* **mysql/**: Contains `my.cnf` for custom database performance tuning.
* **outputs/**: Final reports (Excel/PDF) are generated here.
* **report_generator.py**: The main Python application logic.
* **dockerfile & docker-compose.yml**: Instructions for containerization.
* **config.yaml**: Business logic settings (VAT, exclusions).
* **requirements.txt**: Python library dependencies.
* **extra/**:Side-storage for data and files kept for future reference or secondary use.
* **dags/, plugins/, logs/**: `Airflow` directories for future task orchestration.
* **CONFIG_GUIDE.md**: Detailed instructions on modifying system settings.

---

## 3. Installation Steps

### Step 1: Prepare the Data
Ensure your source data is in the `data/` folder and `sql\` folder. The system expects sales data in CSV format and surface data in XLSX.

### Step 2: Configure Environment Variables
Create a `.env` file in the root directory and define your credentials:
```bash
DB_USER=pfe_user
DB_PASSWORD=your_password
DB_NAME=pfe_db
REPORT_MONTH=03
REPORT_YEAR=2024