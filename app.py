from flask import Flask, request, jsonify
import pandas as pd
import requests
import os
import logging
from datetime import datetime
import validators
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = './uploads'  # Directory for uploaded Excel files
PDF_DOWNLOAD_FOLDER = './pdf_downloads'  # Directory for downloaded PDFs
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Setup folders and logging
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_DOWNLOAD_FOLDER, exist_ok=True)

logging.basicConfig(
    filename=f'download_log_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_excel_format(df):
    required_columns = {'State/Region', 'Report Name', 'Source URL', 'Report Path'}
    return all(col in df.columns for col in required_columns)

@app.route('/upload', methods=['POST'])
def upload_excel():
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            logging.error("No file part in request")
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        # Check if file is selected and has allowed extension
        if file.filename == '':
            logging.error("No file selected")
            return jsonify({"error": "No file selected"}), 400
            
        if not allowed_file(file.filename):
            logging.error(f"Invalid file format: {file.filename}")
            return jsonify({"error": "Unsupported file format. Please upload .xlsx or .xls"}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        logging.info(f"File uploaded successfully: {filename}")

        # Read and validate Excel file
        try:
            df = pd.read_excel(file_path)
            if not validate_excel_format(df):
                logging.error("Invalid Excel format: missing required columns")
                return jsonify({"error": "Excel file missing required columns"}), 400
            
            if df.empty:
                logging.error("Empty Excel file")
                return jsonify({"error": "Excel file is empty"}), 400
                
        except Exception as e:
            logging.error(f"Error reading Excel file: {str(e)}")
            return jsonify({"error": f"Error reading Excel file: {str(e)}"}), 500

        # Process each row
        successful_downloads = 0
        failed_downloads = 0

        for index, row in df.iterrows():
            try:
                state = str(row['State/Region']).strip()
                report_name = str(row['Report Name']).strip()
                source_url = str(row['Source URL']).strip()
                pdf_path = str(row['Report Path']).strip()

                # Validate URL
                if not validators.url(source_url):
                    logging.error(f"Invalid URL at row {index}: {source_url}")
                    failed_downloads += 1
                    continue

                # Download PDF with timeout and headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(source_url, timeout=10, headers=headers)
                
                if response.status_code != 200:
                    logging.error(f"Failed to download from {source_url}: Status {response.status_code}")
                    failed_downloads += 1
                    continue

                # Check if content is a PDF
                content_type = response.headers.get('Content-Type', '').lower()
                content = response.content[:100]  # Check first 100 bytes
                if 'application/pdf' not in content_type and not content.startswith(b'%PDF-'):
                    logging.error(f"URL {source_url} at row {index} returned non-PDF content (Content-Type: {content_type})")
                    failed_downloads += 1
                    continue

                # Create filename and save PDF
                pdf_name = f"{state}_{report_name}.pdf"
                sanitized_pdf_name = secure_filename(pdf_name)
                local_pdf_path = os.path.join(PDF_DOWNLOAD_FOLDER, sanitized_pdf_name)

                with open(local_pdf_path, 'wb') as pdf_file:
                    pdf_file.write(response.content)

                logging.info(f"Successfully downloaded: {sanitized_pdf_name} from {source_url}")
                successful_downloads += 1

            except requests.RequestException as e:
                logging.error(f"Download failed for {source_url}: {str(e)}")
                failed_downloads += 1
                continue
            except Exception as e:
                logging.error(f"Unexpected error at row {index}: {str(e)}")
                failed_downloads += 1
                continue

        # Clean up: remove uploaded Excel file
        try:
            os.remove(file_path)
            logging.info(f"Removed temporary file: {file_path}")
        except Exception as e:
            logging.warning(f"Could not remove temporary file {file_path}: {str(e)}")

        # Prepare response
        response = {
            "message": "Processing completed",
            "successful_downloads": successful_downloads,
            "failed_downloads": failed_downloads,
            "total_processed": len(df)
        }
        
        logging.info(f"Download summary: {response}")
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)