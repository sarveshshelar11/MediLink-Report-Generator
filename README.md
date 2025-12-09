MEDILINK – AUTOMATED PATIENT REPORT GENERATOR

A lightweight system that converts raw Excel patient records into standardized PDF reports. MediLink automates data validation, formatting, and multi-report generation through a simple upload interface.

===================================================================

SECTION 1 — OVERVIEW

Healthcare facilities often manage patient data inside unstructured Excel sheets. Preparing individual reports manually is slow, repetitive, and prone to formatting errors. MediLink eliminates this manual effort by automatically transforming spreadsheet rows into professionally formatted PDF reports. The system uses a React.js frontend and a Python Flask backend, with Pandas for data processing and Jinja2 for template rendering.

===================================================================

SECTION 2 — PROBLEM STATEMENT

Smaller clinics and diagnostic centers frequently rely on Excel-based workflows. This introduces several challenges:

• Manual formatting of patient reports consumes staff time
• High chances of human error when handling inconsistent data
• No guaranteed standard format across departments
• Difficult to generate multiple reports quickly

MediLink solves this by providing an automated and reliable mechanism for converting raw Excel data into clean, standardized PDF reports.

===================================================================

SECTION 3 — KEY FEATURES

• AUTOMATED PDF GENERATION
Converts each patient record (row) into an individual PDF.

• BULK PROCESSING
Generates multiple reports at once and returns them inside a ZIP file.

• TEMPLATE-DRIVEN DESIGN
Layout and styling are controlled through a reusable HTML + CSS template.

• DATA CLEANUP
Missing values are replaced with placeholders to ensure consistent output.

• SIMPLE USER INTERFACE
Upload Excel → Receive ZIP → Download.

• MODULAR BACKEND
Separate folders for uploads, templates, and generated reports.

===================================================================

SECTION 4 — SYSTEM ARCHITECTURE

FRONTEND (REACT.JS)
• Provides file-upload interface
• Sends Excel file to backend using Fetch API
• Receives a ZIP file of generated PDFs

BACKEND (FLASK + PYTHON)
• Receives Excel file
• Reads and cleans data with Pandas
• Renders patient data into HTML via Jinja2
• Converts HTML to PDF using pdfkit + wkhtmltopdf
• Compresses all generated PDFs into a ZIP archive

WORKFLOW (TEXT DIAGRAM)
React Upload
↓
Flask API Receives File
↓
Pandas Validates + Cleans Data
↓
Jinja2 HTML Rendering
↓
PDF Generation via pdfkit
↓
ZIP Packaging
↓
React Download

===================================================================

SECTION 5 — TECHNOLOGY STACK

FRONTEND TECHNOLOGIES
• React.js
• Fetch API

BACKEND TECHNOLOGIES
• Python Flask
• Pandas
• openpyxl
• Jinja2
• pdfkit + wkhtmltopdf

FILE CONVERSION
• wkhtmltopdf engine for HTML → PDF conversion

===================================================================

SECTION 6 — FOLDER STRUCTURE

MediLink/
  backend/
    app.py
    templates/
      report_template.html
    uploads/
    generated_pdfs/
    wkhtmlpdf/
      wkhtmltopdf.exe

  frontend/
    src/
      App.js
      (other React files)
    public/
    package.json



===================================================================

SECTION 7 — INSTALLATION AND SETUP

STEP 1 — CLONE REPOSITORY
git clone https://github.com/sarveshshelar11/MediLink-Report-Generator.git

cd MediLink-Report-Generator

STEP 2 — BACKEND SETUP
cd backend
python -m venv .venv
..venv\Scripts\activate
pip install -r requirements.txt

Ensure wkhtmltopdf.exe exists in:
backend/wkhtmlpdf/

Run backend:
python app.py

STEP 3 — FRONTEND SETUP
cd ../frontend
npm install
npm start

===================================================================

SECTION 8 — USAGE

Open the React interface

Upload an Excel (.xlsx) file

Backend processes each row

System generates PDFs

ZIP file is returned for download

===================================================================

SECTION 9 — TESTING

FUNCTIONAL TESTING
• Valid Excel with correct columns → ZIP generated
• Missing columns → Error returned
• Large datasets → System performance verified
• Invalid file types → Rejected

UNIT TESTING
• Excel reading
• Data cleanup
• HTML rendering
• PDF generation

===================================================================

SECTION 10 — LIMITATIONS

• Requires wkhtmltopdf installation
• Excel must contain correct column names
• No authentication system
• No support for custom templates from frontend

===================================================================

SECTION 11 — FUTURE IMPROVEMENTS

• Database integration for stored records
• Role-based login for doctors/staff
• Multiple layout templates
• Browser-based PDF preview
• REST API integration with hospital systems

THNAK YOU !!!

In LMS submissions

Because it avoids Markdown-heavy styling.
