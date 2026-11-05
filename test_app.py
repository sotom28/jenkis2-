from app import app


def test_health():
    r = app.test_client().get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_hello():
    r = app.test_client().get("/hello?name=ana")
    assert r.status_code == 200
    assert b"Hello, ana!" in r.data
