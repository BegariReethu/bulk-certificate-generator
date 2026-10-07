from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, SessionLocal
from .models import GenerationJob, Recipient
from .schemas import GenerationRequest, JobCreateResponse, JobStatusResponse
from .services import GENERATED_DIR, generate_certificate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator", version="1.0.0")

# Prevent two workers in this simple assignment from updating the same SQLite
# job counters at exactly the same time.
job_lock = Lock()


def process_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if not job:
            return

        recipients = list(job.recipients)
        for recipient in recipients:
            try:
                output_path = GENERATED_DIR / f"certificate_{recipient.id}.pdf"
                # Individual failures are isolated here deliberately.
                generate_certificate(
                    recipient.name,
                    job.event_name,
                    job.certificate_title,
                    output_path,
                )
                recipient.status = "SUCCESS"
                recipient.certificate_path = str(output_path)
                recipient.error_message = None
                with job_lock:
                    job.successful += 1
            except Exception as exc:  # noqa: BLE001 - record per-recipient failure
                recipient.status = "FAILED"
                recipient.error_message = str(exc)
                with job_lock:
                    job.failed += 1
            db.commit()

        job.status = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs", response_model=JobCreateResponse, status_code=202)
def create_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = GenerationJob(
        event_name=request.event_name,
        certificate_title=request.certificate_title,
        status="PROCESSING",
        total=len(request.recipients),
        successful=0,
        failed=0,
    )
    db.add(job)
    db.flush()

    for item in request.recipients:
        db.add(Recipient(job_id=job.id, name=item.name, email=str(item.email), status="PENDING"))

    db.commit()
    db.refresh(job)
    background_tasks.add_task(process_job, job.id)

    return JobCreateResponse(job_id=job.id, status=job.status, total=job.total)


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")

    progress = ((job.successful + job.failed) / job.total * 100) if job.total else 100.0
    certificates = [
        {
            "id": recipient.id,
            "recipient_name": recipient.name,
            "email": recipient.email,
            "status": recipient.status,
            "error_message": recipient.error_message,
            "download_url": f"/certificates/{recipient.id}"
            if recipient.status == "SUCCESS"
            else None,
        }
        for recipient in job.recipients
    ]

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        total=job.total,
        successful=job.successful,
        failed=job.failed,
        progress=round(progress, 2),
        certificates=certificates,
    )


@app.get("/certificates/{recipient_id}")
def get_certificate(recipient_id: int, db: Session = Depends(get_db)):
    recipient = db.get(Recipient, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if recipient.status != "SUCCESS" or not recipient.certificate_path:
        raise HTTPException(status_code=409, detail="Certificate is not available")

    path = Path(recipient.certificate_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Generated certificate file is missing")

    return FileResponse(path, media_type="application/pdf", filename=path.name)
