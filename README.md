# 🚀 ERP Report Generator (PFE 2024-2025)

This project is a high-performance automated system designed to process over 16 million rows of sales data from a 7GB MySQL database to generate executive Excel and PDF reports.

## 2. Project Objectives

* **Automation**: Streamline the extraction and transformation of raw ERP data into actionable reports.
* **Scalability**: Handle large datasets (7GB+) efficiently using Docker and optimized MySQL configurations.
* **Communication**: Automatically deliver financial summaries to stakeholders via Gmail or Outlook.
* **Flexibility**: Allow non-technical users to modify business rules via simple configuration files.

## 2. Project Documentation

To manage or deploy this system, please refer to the specific guides below:

* **INSTALLATION_GUIDE.md**: [Step-by-step instructions](./INSTALLATION_GUIDE.md) on how to set up the Docker environment and database.
* **CONFIG_GUIDE.md**: [Instructions](./CONFIG_GUIDE.md) on how to update VAT rates, report periods, and product exclusions.

---

## 3. Quick Start

If your environment is already configured according to the installation guide, use the following commands:

**Run the Database:**
`docker-compose up -d pfe_mysql`

**Generate the Report:**
`docker-compose up report_gen`

---

## 4. PFE Progress Tracker

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Week 1** | Dockerization, Database Setup, and Image creation | ✅ **Completed** |
| **Week 2** | Configuration System, Secret Management, and Documentation | ✅ **Completed** |
| **Week 3** | Automation & Orchestration (Airflow Integration) | ⏳ Upcoming |

---

## 5. Technologies Used
* **Python**: Data processing and report generation.
* **MySQL**: High-capacity data storage.
* **Docker**: Containerization and environment isolation.
* **YAML**: Externalized business logic configuration.