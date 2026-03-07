from fastapi.testclient import TestClient

from src.app import app
from src.storage.db import Base, SessionLocal, engine
from src.storage.models import Tenant


def test_web_chat_endpoint_processes_message():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    tenant = db.query(Tenant).filter(Tenant.id == 1).first()
    if not tenant:
        db.add(Tenant(id=1, name='web', timezone='UTC'))
        db.commit()
    db.close()

    client = TestClient(app)
    resp = client.post('/api/chat', json={'tenant_id': 1, 'text': 'hours', 'session_id': 'session-1'})

    assert resp.status_code == 200
    body = resp.json()
    assert body['status'] == 'processed'
    assert 'Mon-Fri' in body['reply']
