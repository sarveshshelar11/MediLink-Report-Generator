from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import os
import zipfile
from io import BytesIO
import pandas as pd
import pdfkit
from jinja2 import Template
import sys
import re
import shutil
import traceback

# ---------------------- CONFIG ----------------------
app = Flask(__name__, template_folder="templates")
CORS(app)  # allow frontend requests from anywhere (dev). Lock down in production.

# Create required folders if missing
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated_pdfs", exist_ok=True)

# Path to wkhtmltopdf (adjust if needed)
WKHTMLTOPDF_PATH = r"S:\MediLink\backend\wkhtmltopdf\wkhtmltopdf.exe"

use_wkhtml = True
if not os.path.exists(WKHTMLTOPDF_PATH):
    # Try common windows path as fallback (optional)
    alt = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if os.path.exists(alt):
        WKHTMLTOPDF_PATH = alt
    else:
        use_wkhtml = False
        print("WARNING: wkhtmltopdf not found. pdfkit/wkhtmltopdf will not be available.")

if use_wkhtml:
    try:
        config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    except Exception as e:
        print("Error configuring pdfkit:", e)
        use_wkhtml = False
else:
    config = None


def safe_filename(s: str) -> str:
    """Make a filesystem-safe filename from an arbitrary string."""
    if not s:
        s = "patient"
    s = str(s)
    s = s.strip()
    s = re.sub(r"[^\w\s-]", "", s)        # remove non-word chars
    s = re.sub(r"[-\s]+", "_", s)         # replace spaces and hyphens
    return s[:200]                        # limit length

def normalize_record_keys(record: dict) -> dict:
    """
    Return a copy with normalized keys: lowercase, spaces -> underscores.
    This helps match template variables like {{ name }} etc.
    """
    return { re.sub(r"\s+", "_", k.strip().lower()): v for k, v in record.items() if k is not None }

def render_html(data: dict) -> str:
    """Renders the patient data into an HTML template."""
    template_path = os.path.join("templates", "report_template.html")
    if not os.path.exists(template_path):
        raise FileNotFoundError("report_template.html not found in templates/ directory.")
    with open(template_path, 'r', encoding='utf-8') as f:
        template = Template(f.read())
    return template.render(**data)

def generate_pdf_from_html(html: str, safe_name: str) -> str:
    """Generates a single PDF from HTML using pdfkit (wkhtmltopdf)."""
    output_path = os.path.join("generated_pdfs", f"{safe_name}_Report.pdf")
    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not use_wkhtml:
        raise RuntimeError("wkhtmltopdf is not available on the system. Install it or configure path.")

    # pdfkit options - enable local file access for CSS etc.
    options = {
        "enable-local-file-access": None,
        "page-size": "A4",
        "margin-top": "15mm",
        "margin-bottom": "15mm",
        "margin-left": "12mm",
        "margin-right": "12mm",
    }

    # Generate PDF (this may raise an IOError on failure)
    pdfkit.from_string(html, output_path, configuration=config, options=options)
    return output_path

# ---------------------- ROUTES ----------------------

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "MediLink Patient Report API is running"})

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        # Save uploaded file
        upload_path = os.path.join('uploads', safe_filename(file.filename))
        file.save(upload_path)

        # Read excel - allow engine autodetect; handle CSV fallback
        try:
            df = pd.read_excel(upload_path)
        except Exception as e_excel:
            try:
                df = pd.read_csv(upload_path)
            except Exception:
                # cleanup uploaded file
                os.remove(upload_path)
                return jsonify({'error': 'Invalid file format. Upload a valid Excel (.xlsx) file.'}), 400

        # Normalize column names to lowercase and underscores
        df.columns = [re.sub(r"\s+", "_", str(c).strip().lower()) for c in df.columns]

        # Accept 'name' or alternatives
        if 'name' not in df.columns:
            # try common alternatives
            alt_candidates = ['full_name', 'patient_name']
            if not any(col in df.columns for col in alt_candidates):
                os.remove(upload_path)
                return jsonify({'error': 'Excel must contain a column named "name" (or "full name").'}), 400

        # Create ZIP in memory
        output_zip = BytesIO()
        generated_paths = []
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, row in df.iterrows():
                # Turn row into dict and normalize keys
                record = row.fillna("N/A").to_dict()
                record = normalize_record_keys(record)

                # Determine name (fallback to index if missing)
                name_key_candidates = ['name', 'full_name', 'patient_name']
                patient_name = None
                for k in name_key_candidates:
                    if k in record and record[k] and str(record[k]).strip().upper() != "N/A":
                        patient_name = record[k]
                        break
                if not patient_name:
                    patient_name = f"patient_{idx+1}"

                # Make safe and unique name
                safe_name_base = safe_filename(patient_name)
                safe_name = f"{safe_name_base}_{idx+1}"

                # Render HTML and generate PDF
                try:
                    html = render_html(record)
                except Exception as e:
                    # log to server console
                    traceback.print_exc()
                    continue  # skip this record but continue others

                try:
                    pdf_path = generate_pdf_from_html(html, safe_name)
                except Exception as e:
                    # Log and return error with some detail for debugging
                    traceback.print_exc()
                    # cleanup generated files so far
                    for p in generated_paths:
                        try:
                            os.remove(p)
                        except Exception:
                            pass
                    os.remove(upload_path)
                    return jsonify({'error': 'PDF generation failed', 'detail': str(e)}), 500

                generated_paths.append(pdf_path)
                zipf.write(pdf_path, arcname=os.path.basename(pdf_path))

        # cleanup uploaded file (we keep generated_pdfs until zipped)
        if os.path.exists(upload_path):
            try:
                os.remove(upload_path)
            except Exception:
                pass

        # prepare zip for sending
        output_zip.seek(0)

        # After sending, optionally cleanup generated PDFs (we'll delete them now)
        response = send_file(
            output_zip,
            mimetype='application/zip',
            as_attachment=True,
            download_name='Patient_Reports.zip'
        )

        # schedule cleanup of generated PDFs now (best-effort)
        for p in generated_paths:
            try:
                os.remove(p)
            except Exception:
                pass

        return response

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

# --------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
