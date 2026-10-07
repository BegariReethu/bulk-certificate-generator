from pathlib import Path

from app.services import generate_certificate


def test_certificate_generation(tmp_path):
    output = tmp_path / "certificate.pdf"
    generate_certificate(
        "Test User",
        "Python Workshop",
        "Certificate of Completion",
        output,
    )
    assert output.exists()
    assert output.stat().st_size > 0
    assert output.read_bytes().startswith(b"%PDF")


def test_certificate_retrieval(client):
    payload = {
        "event_name": "Python Workshop",
        "recipients": [{"name": "Test User", "email": "test@example.com"}],
    }
    created = client.post("/jobs", json=payload).json()
    job = client.get(f"/jobs/{created['job_id']}").json()
    certificate_id = job["certificates"][0]["id"]

    response = client.get(f"/certificates/{certificate_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
