
def test_invalid_email_is_rejected(client):
    payload = {
        "event_name": "Python Workshop",
        "recipients": [{"name": "Rahul Sharma", "email": "not-an-email"}],
    }
    response = client.post("/jobs", json=payload)
    assert response.status_code == 422


def test_empty_recipient_list_is_rejected(client):
    payload = {"event_name": "Python Workshop", "recipients": []}
    response = client.post("/jobs", json=payload)
    assert response.status_code == 422


def test_blank_name_is_rejected(client):
    payload = {
        "event_name": "Python Workshop",
        "recipients": [{"name": "  ", "email": "a@example.com"}],
    }
    response = client.post("/jobs", json=payload)
    assert response.status_code == 422
