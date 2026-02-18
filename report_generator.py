import os
import sys
import time
import pandas as pd
import numpy as np
import yaml
import calendar
import warnings
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from fpdf import FPDF
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# 1. SETUP & LOGGING
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv() 
OUTPUT_DIR = "/app/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# SMTP Config
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASSWORD")

print("=== STARTING OPTIMIZED REPORT GENERATION ===")

# 2. CONFIGURATION & PARAMS
try:
    with open("/app/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    print("✔ Configuration loaded successfully")
except Exception as e:
    print(f"CRITICAL: Error loading config.yaml: {e}")
    sys.exit(1)

# Get Distribution Info from YAML
dist_list = config.get('mail_distribution', [])
if not dist_list:
    print("CRITICAL: mail_distribution section is empty in config.yaml")
    sys.exit(1)

current_dist = dist_list[0]
RECIPIENTS = current_dist.get('recipients', []) 
CUSTOM_FILE_NAME = current_dist.get('file_name', 'Report')

# DB Params
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "3306")

TARGET_MONTH = os.getenv("REPORT_MONTH", "09")
TARGET_YEAR = os.getenv("REPORT_YEAR", "2024")

# Business Rules
VAT_RATE = config['business_rules']['vat_rate']
EXCLUDED = config['business_rules']['excluded_families']
FALLBACK_MARGIN = config['business_rules']['margin_fallback']
vat_divisor = 1 + (VAT_RATE / 100)
start_time = datetime.now()

# 3. DATABASE CONNECTION
def connect_to_database(max_retries=10, retry_interval=10):
    connection_string = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(connection_string, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM histovente LIMIT 1"))
                print(f"✔ Database ready")
                return engine
        except Exception:
            print(f"⏳ Waiting for database... (Attempt {attempt}/{max_retries})")
            time.sleep(retry_interval)
    sys.exit(1)

engine = connect_to_database()

# 4. DATA PROCESSING
last_day = calendar.monthrange(int(TARGET_YEAR), int(TARGET_MONTH))[1]
start_date = f"{TARGET_YEAR}-{TARGET_MONTH}-01"
end_date = f"{TARGET_YEAR}-{TARGET_MONTH}-{last_day}"

excluded_str = "', '".join(EXCLUDED)
sql_query = f"""
SELECT 
    h.CodeMag AS StoreCode, 
    h.Quantite AS Quantity, 
    h.total AS TotalTTC,
    ROUND(h.total / {vat_divisor}, 2) AS TotalHT,
    (a.PrixAchat * h.Quantite) AS PurchasePrice
FROM histovente h
LEFT JOIN (
    SELECT CodeBarre, MAX(IdEntite) as IdEntite 
    FROM codebarre 
    GROUP BY CodeBarre
) c ON c.CodeBarre = h.Barcode 
LEFT JOIN article a ON a.IDArticle = c.IdEntite 
WHERE h.reception BETWEEN '{start_date}' AND '{end_date}'
AND h.typevente IN ('Avoir', 'Vente')
AND h.Famille NOT IN ('{excluded_str}');
"""

print(f"🚀 Pulling {TARGET_MONTH}/{TARGET_YEAR} data...")
df_sql = pd.read_sql(sql_query, engine)

# 5. AGGREGATION & KPIs
ca = df_sql.groupby(['StoreCode'])[['Quantity', 'TotalHT', 'PurchasePrice']].sum().reset_index()
ca['PurchasePrice'] = ca['PurchasePrice'].replace(0, np.nan).fillna(ca['TotalHT'] * (1 - FALLBACK_MARGIN))
ca['Profit'] = (ca['TotalHT'] - ca['PurchasePrice']).round(2)
ca['GP %'] = ((ca['Profit'] / ca['TotalHT']) * 100).replace([np.inf, -np.inf], 0).fillna(0).round(2)

# 6. OUTPUT GENERATION
excel_file = os.path.join(OUTPUT_DIR, f'{CUSTOM_FILE_NAME}.xlsx')
pdf_path = os.path.join(OUTPUT_DIR, f'{CUSTOM_FILE_NAME}.pdf')

# Excel
ca.sort_values('TotalHT', ascending=False).to_excel(excel_file, index=False)
print(f"✔ Excel Saved")

# PDF
class PDF(FPDF):
    def header(self):
        self.set_fill_color(44, 62, 80)  # Dark Blue-Grey
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 18)
        self.cell(0, 20, 'ERP PERFORMANCE REPORT', ln=True, align='C')
        self.ln(10)

    def draw_table(self, df):
        # Table Header
        self.set_fill_color(200, 200, 200)
        self.set_text_color(0)
        self.set_font('helvetica', 'B', 10)
        
        # Define column widths
        w = [40, 50, 50, 40]
        cols = ["Store Code", "Revenue (HT)", "Profit", "GP %"]
        
        for i, col in enumerate(cols):
            self.cell(w[i], 10, col, 1, 0, 'C', True)
        self.ln()

        # Table Rows
        self.set_font('helvetica', '', 10)
        for _, row in df.iterrows():
            self.cell(w[0], 10, str(row['StoreCode']), 1, 0, 'C')
            self.cell(w[1], 10, f"{row['TotalHT']:,.2f}", 1, 0, 'R')
            self.cell(w[2], 10, f"{row['Profit']:,.2f}", 1, 0, 'R')
            self.cell(w[3], 10, f"{row['GP %']}%", 1, 0, 'C')
            self.ln()
            
        # Add a Total Row
        self.set_font('helvetica', 'B', 10)
        self.set_fill_color(240, 240, 240)
        self.cell(w[0], 10, "TOTAL", 1, 0, 'C', True)
        self.cell(w[1], 10, f"{df['TotalHT'].sum():,.2f}", 1, 0, 'R', True)
        self.cell(w[2], 10, f"{df['Profit'].sum():,.2f}", 1, 0, 'R', True)
        self.cell(w[3], 10, "", 1, 1, 'C', True)

# Generate PDF
try:
    pdf = PDF()
    pdf.add_page()
    pdf.set_text_color(0)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"Report Name: {CUSTOM_FILE_NAME}", ln=True)
    pdf.cell(0, 10, f"Period: {TARGET_MONTH}/{TARGET_YEAR}", ln=True)
    pdf.ln(5)

    # Filter top 30 stores for the PDF to keep it readable, or send full df
    pdf.draw_table(ca.sort_values('TotalHT', ascending=False).head(30))
    
    pdf.output(pdf_path)
    print(f"✔ PDF Saved with Data")
except Exception as e:
    print(f"✗ PDF Error: {e}")

# 7. EMAIL DELIVERY
def send_report_email(file_paths, recipients):
    if not recipients:
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER 
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"🚀 {CUSTOM_FILE_NAME} - {TARGET_MONTH}/{TARGET_YEAR}"

        msg.attach(MIMEText(f"Attached is the {CUSTOM_FILE_NAME}.", 'plain'))

        for path in file_paths:
            with open(path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
                msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ Success! Reports sent to: {recipients}")
    except Exception as e:
        print(f"❌ SMTP Error: {e}")

# Finish
engine.dispose()
send_report_email([excel_file, pdf_path], RECIPIENTS)
print(f"--- FINISH: Runtime: {datetime.now() - start_time} ---")