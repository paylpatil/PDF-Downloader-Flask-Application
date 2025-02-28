# PDF Downloader Flask Application

## Overview
This Flask application allows users to upload an Excel file containing PDF source URLs, and the application downloads the PDFs automatically. The application also validates the uploaded Excel file and logs all download activities.

## Features
- Accepts `.xlsx` and `.xls` files containing PDF URLs.
- Validates the format of the uploaded Excel file.
- Downloads PDFs from valid URLs and stores them locally.
- Logs all upload and download activities.
- Returns a summary of successful and failed downloads.

## Requirements
Make sure you have Python installed (>=3.7) and install the required dependencies:

```sh
pip install flask pandas requests validators openpyxl werkzeug
```

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/pdf-downloader.git
   cd pdf-downloader
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the application:
   ```sh
   python app.py
   ```

## API Endpoints
### Upload Excel File
**Endpoint:** `/upload`  
**Method:** `POST`  
**Description:** Upload an Excel file containing PDF URLs.

#### Request Format
- `file`: Excel file (`.xlsx` or `.xls`)

#### Response Format
```json
{
  "message": "Processing completed",
  "successful_downloads": 5,
  "failed_downloads": 2,
  "total_processed": 7
}
```

## Expected Excel Format
| State/Region | Report Name | Source URL | Report Path |
|-------------|------------|------------|-------------|
| Maharashtra | Report_1   | http://example.com/report1.pdf | /path/to/report1 |
| Karnataka   | Report_2   | http://example.com/report2.pdf | /path/to/report2 |

- The file must contain these four columns: `State/Region`, `Report Name`, `Source URL`, and `Report Path`.

## File Storage
- Uploaded Excel files are temporarily stored in `./uploads/` and deleted after processing.
- Downloaded PDFs are saved in `./pdf_downloads/`.

## License
This project is licensed under the MIT License.

