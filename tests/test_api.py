from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """
    /health endpoint'inin çalışabilirliğini ve 
    servis mesajının doğruluğunu test eder.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert "message" in response.json()

def test_ask_valid_query():
    """
    Geçerli bir soruda sistemin 200 dönüp dönmediğini 
    ve metadata yapısını kontrol eder.
    """
    response = client.get("/ask?query=Y İnovasyon nedir?")
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "metadata" in data
    assert "processing_time_sec" in data["metadata"]

def test_ask_empty_query():
    """
    Soru boş gönderildiğinde FastAPI validation hatası (422) 
    alındığını teyit eder.
    """
    response = client.get("/ask?query=")
    # FastAPI, min_length=3 kuralına uymayan girişler için otomatik 422 döner
    assert response.status_code == 422
    assert "detail" in response.json()

def test_ask_short_query():
    """
    FastAPI validation kuralına (min_length=3) göre 
    çok kısa soruların reddedildiğini test eder.
    """
    response = client.get("/ask?query=ab")
    assert response.status_code == 422

def test_index_endpoint():
    """
    İndeksleme mekanizmasının tetiklenebilirliğini test eder.
    """
    response = client.get("/index")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "success"
    