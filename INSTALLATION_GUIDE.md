# 🛠️ Installation & Setup Guide

This document describes how to deploy the development and production environment for the ERP Report Generator.

## 1. Prerequisites
To run this project, you must have the following installed on your machine:
* **Docker Desktop** (for Windows/Mac) or **Docker Engine** (for Linux).
* **Docker Compose V2**.
* At least **15GB of free disk space** (to accommodate the 16M rows database volume).

## 2. Project Directory Overview
The project is organized to separate data, logic, and infrastructure:

* **data/**: Source files (CSV/Excel).
* **sql/**: Contains `DB.sql` (Main schema).
* **mysql/**: Custom `my.cnf` for performance tuning.
* **outputs/**: Final reports (Excel/PDF) are generated here.
* **report_generator.py**: Main Python application logic.
* **config.yaml**: Business logic settings and Email recipients.
* **extra/**: Side-storage for backup files.
* **dags/, plugins/, logs/**: Airflow directories for Week 3 orchestration.

---

## 3. Installation Steps

### Step 1: Prepare the Data
Ensure your source data is in the `data/` folder. The system expects sales data in CSV and surface data in XLSX.

### Step 2: Configure Environment Variables
Create a `.env` file in the root directory. This file is ignored by Git for security:

```bash
# Database Settings
DB_USER=pfe_user
DB_PASSWORD=your_password
DB_NAME=pfe_db

# Report Settings
REPORT_MONTH=11
REPORT_YEAR=2023

# SMTP Settings
SMTP_SERVER=smtp.gmail.com # or smtp.office365.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx # Use App Password