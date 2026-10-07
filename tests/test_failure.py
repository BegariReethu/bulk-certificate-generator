import app.main as main_module


def test_individual_certificate_failure_does_not_stop_job(client, monkeypatch):
    original = main_module.generate_certificate

    def failing_generator(name, event_name, certificate_title, output_path):
        if name == "Bad User":
            raise RuntimeError("simulated generation failure")
        return original(name, event_name, certificate_title, output_path)

    monkeypatch.setattr(main_module, "generate_certificate", failing_generator)

    payload = {
        "event_name": "Python Workshop",
        "recipients": [
            {"name": "Bad User", "email": "bad@example.com"},
            {"name": "Good User", "email": "good@example.com"},
        ],
    }
    created = client.post("/jobs", json=payload).json()
    job = client.get(f"/jobs/{created['job_id']}").json()

    assert job["status"] == "COMPLETED"
    assert job["successful"] == 1
    assert job["failed"] == 1
    assert job["progress"] == 100.0

    results = {item["recipient_name"]: item for item in job["certificates"]}
    assert results["Bad User"]["status"] == "FAILED"
    assert "simulated generation failure" in results["Bad User"]["error_message"]
    assert results["Good User"]["status"] == "SUCCESS"
