from fastapi.testclient import TestClient
import models
from auth import create_access_token

def test_get_audit_logs_user(client: TestClient, db):
    user = models.User(username="audituser", email="audit@test.com", role="Doctor")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add an audit log manually
    log = models.AuditLog(user_id=user.id, action="TEST_ACTION", status="SUCCESS")
    db.add(log)
    db.commit()
    
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/identity/audit/logs", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["action"] == "TEST_ACTION"

def test_get_all_audit_logs_super_admin(client: TestClient, db):
    admin_user = models.User(username="auditadmin", email="auditadmin@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/identity/audit/logs/all", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_all_audit_logs_forbidden(client: TestClient, db):
    doc_user = models.User(username="auditdoc", email="auditdoc@test.com", role="Doctor")
    db.add(doc_user)
    db.commit()
    
    token = create_access_token(data={"sub": doc_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/identity/audit/logs/all", headers=headers)
    assert response.status_code == 403
