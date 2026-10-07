# Bulk Certificate Generator

A small backend API for generating certificates for many recipients in one request.

## Technology

- Python
- FastAPI
- SQLite (relational database)
- SQLAlchemy
- ReportLab for PDF generation
- pytest for automated tests

No frontend is required.

## Features

- Submit one bulk certificate generation request.
- Validate recipient names and email addresses.
- Process recipients in the background.
- Generate an individual PDF for each successful recipient.
- Track job status, total, successful, failed, and progress percentage.
- A failure for one recipient does not stop other recipients.
- Retrieve generated certificates through an API endpoint.

## Project structure

```text
bulk-certificate-generator/
├── app/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
├── generated/
├── tests/
├── requirements.txt
└── README.md
```

## Setup

Python 3.10+ is recommended.

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

FastAPI's interactive API documentation is available at `/docs`.

## Submit a generation request

```http
POST /jobs
```

Example JSON:

```json
{
  "event_name": "Python Workshop 2026",
  "certificate_title": "Certificate of Completion",
  "recipients": [
    {
      "name": "Rahul Sharma",
      "email": "rahul@example.com"
    },
    {
      "name": "Priya Reddy",
      "email": "priya@example.com"
    }
  ]
}
```

The API immediately returns a job ID:

```json
{
  "job_id": 1,
  "status": "PROCESSING",
  "total": 2
}
```

The endpoint returns HTTP 202 because generation is performed as background work.

## Check job status

```http
GET /jobs/{job_id}
```

Example:

```json
{
  "job_id": 1,
  "status": "COMPLETED",
  "total": 2,
  "successful": 2,
  "failed": 0,
  "progress": 100.0,
  "certificates": [
    {
      "id": 1,
      "recipient_name": "Rahul Sharma",
      "email": "rahul@example.com",
      "status": "SUCCESS",
      "error_message": null,
      "download_url": "/certificates/1"
    }
  ]
}
```

Progress is calculated as:

`(successful + failed) / total * 100`

A failed recipient therefore still contributes to job progress, because processing that recipient has finished.

## Retrieve a certificate

```http
GET /certificates/{recipient_id}
```

The endpoint returns the generated PDF file.

## Validation and failure handling

Request-level validation is handled by Pydantic/FastAPI. Invalid email addresses, empty recipient lists, and invalid names result in HTTP 422.

Generation failures are handled per recipient. The service catches an exception for the individual recipient, stores `FAILED` and an error message, and continues with the next recipient.

## Design decisions

### Why FastAPI?

FastAPI provides a clean Python REST API, automatic request validation, and automatic API documentation. It also makes the application easy to test.

### Why SQLite?

The assignment only requires a relational database. SQLite keeps the project easy to run without requiring a separate database server. The data model can later be migrated to PostgreSQL if needed.

### Why background processing?

A bulk request should not require the client to wait for every PDF. The API creates the job and recipient records first, returns a job ID, and then performs generation in background processing.

For a production system handling very large workloads, a dedicated worker/queue system could replace FastAPI BackgroundTasks. That is intentionally not included because it is outside the assignment requirements.

### Why ReportLab?

The requirement allows the certificate format and generation library to be chosen freely. ReportLab provides direct PDF generation in Python without requiring a frontend or external service.

## Run tests

```bash
pytest -q
```

The test suite covers:

- Creating a generation job
- Input validation
- Certificate generation
- Job status and progress
- Individual certificate failure handling
- Certificate retrieval
