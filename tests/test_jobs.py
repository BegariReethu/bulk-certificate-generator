def sample_payload():
    return {
        "event_name": "Python Workshop 2026",
        "certificate_title": "Certificate of Completion",
        "recipients": [
            {"name": "Rahul Sharma", "email": "rahul@example.com"},
            {"name": "Priya Reddy", "email": "priya@example.com"},
        ],
    }


def test_create_generation_job(client):
    response = client.post("/jobs", json=sample_payload())
    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] > 0
    assert data["status"] == "PROCESSING"
    assert data["total"] == 2


def test_job_status_progress(client):
    response = client.post("/jobs", json=sample_payload())
    job_id = response.json()["job_id"]

    # TestClient executes BackgroundTasks before returning the response.
    status = client.get(f"/jobs/{job_id}")
    assert status.status_code == 200
    data = status.json()
    assert data["status"] == "COMPLETED"
    assert data["successful"] == 2
    assert data["failed"] == 0
    assert data["progress"] == 100.0
