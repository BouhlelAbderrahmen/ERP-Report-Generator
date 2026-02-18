# 📘 Configuration Guide

This document explains how to manage the report generator settings without modifying the Python source code.

## 1. Business Logic (`config.yaml`)
The `config.yaml` file defines the "Business Rules." It is used for parameters that remain relatively stable but might need adjustment by an administrator.

### Section: `business_rules`
* **`vat_rate`**: The VAT multiplier used for tax calculations (e.g., `0.19` for 19%).
* **`margin_target`**: The target margin percentage. If a row's margin falls below this, it is highlighted in the Excel report.

### Section: `filters`
* **`excluded_families`**: A list of category codes (e.g., `['F01', 'F99']`) to ignore. These items will be filtered out of the final sales calculations.

### Section: `email`
* **`enabled`**: Set to `true` to send emails, or `false` to generate files locally only.

  ```yaml
  email_notifications:
    enabled: true
    recipients:
      - admin@company.com
      - stakeholder@company.com
---
**`recipients`**: A list of emails that will receive the reports.
**`file_name:`** The custom name for the PDF and Excel attachments (e.g., Monthly_Sales_C001).
```yaml
mail_distribution:
  - recipients: 
      - "admin@company.com"
      - "stakeholder@company.com"
    file_name: "Monthly_Sales_Report"

## 2. Environment & Secrets (`.env`)
The `.env` file handles sensitive security information and variables that change frequently (like the target date).

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DB_PASSWORD` | The password for the MySQL database. | `my_secret_pass` |
| `REPORT_MONTH` | The target month for the report. | `03` (for March) |
| `REPORT_YEAR` | The target year for the report. | `2024` |

---

## 3. Standard Procedures

### Scenario: Changing the Report Period
To generate a report for a different month (e.g., moving from September to March):
1. Open the `.env` file.
2. Change `REPORT_MONTH=09` to `REPORT_MONTH=03`.
3. Save the file.
4. Run: `docker-compose up report_gen`.

### Scenario: Updating the Tax Rate
If the government changes the VAT rate from 19% to 20%:
1. Open `config.yaml`.
2. Locate the `vat_rate` key and change it to `0.20`.
3. Save the file.
4. The change will take effect automatically the next time the container runs.

### Standard Procedures
Scenario: **Changing the Report Period**
To generate a report for a different month:
-Open the .env file.
-Update REPORT_MONTH and REPORT_YEAR.
-Save and run: docker-compose up --build report_gen.

Scenario: **Adding a Recipient**
-Open config.yaml.
-Add a new line under recipients following the - email@addr.com format.
-Save the file.

Scenario: **Switching Email Providers (Gmail to Outlook)**
-Open .env.
-Change SMTP_SERVER to smtp.office365.com.
-Update SMTP_USER to your University/Outlook mail.
-Replace SMTP_PASSWORD with the specific App Password for that account.

---

## 4. Technical Safety
The Python script validates these files at startup using a custom configuration loader. If a required variable is missing or the SMTP credentials are incorrect, the script will log a detailed error and halt to prevent generating or distributing incorrect financial data.