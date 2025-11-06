from flask import Flask, request, send_file
from flask_cors import CORS
import pandas as pd
import pdfkit
from jinja2 import Template
import os

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    df = pd.read_excel(file)
    df = df.fillna('N/A')

    html_template = '''
    <html><head><title>Patient Report</title></head><body>
    {% for _, row in df.iterrows() %}
        <h2>Patient Report</h2>
        <p><b>Name:</b> {{ row['name'] }}</p>
        <p><b>Age:</b> {{ row['age'] }}</p>
        <p><b>Sex:</b> {{ row['sex'] }}</p>
        <p><b>Blood Type:</b> {{ row['blood_type'] }}</p>
        <p><b>Diagnosis:</b> {{ row['diagnosis'] }}</p>
        <p><b>Notes:</b> {{ row['notes'] }}</p>
        <p><b>Date:</b> {{ row['test_date'] }}</p>
        <hr>
    {% endfor %}
    </body></html>
    '''
    template = Template(html_template)
    html_content = template.render(df=df)
    output_path = os.path.join('output', 'Patient_Report.pdf')
    pdfkit.from_string(html_content, output_path)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)