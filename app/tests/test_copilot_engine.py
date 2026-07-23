import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from ai_pipeline.copilot_engine import check_prescription_safety, generate_case_history, compare_medical_reports
import json

@patch("ai_pipeline.copilot_engine.client")
def test_check_prescription_safety(mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "warnings": [
            {"alert_type": "ALLERGY", "severity": "HIGH", "message": "Patient is allergic to Penicillin."}
        ]
    })
    mock_client.chat.completions.create.return_value = mock_response

    allergies = [{"allergen": "Penicillin"}]
    current = []
    proposed = [{"name": "Amoxicillin"}]
    
    warnings = check_prescription_safety(1, allergies, current, proposed)
    
    assert len(warnings) == 1
    assert warnings[0]["alert_type"] == "ALLERGY"
    assert "Penicillin" in warnings[0]["message"]

@patch("ai_pipeline.copilot_engine.client")
def test_generate_case_history(mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Patient has a history of diabetes."
    mock_client.chat.completions.create.return_value = mock_response

    history = generate_case_history([], [], [{"name": "Diabetes"}])
    
    assert "history of diabetes" in history

@patch("ai_pipeline.copilot_engine.client")
def test_compare_medical_reports(mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "- Improvement in WBC count"
    mock_client.chat.completions.create.return_value = mock_response

    report_a = {"WBC": 12.0}
    report_b = {"WBC": 7.5}
    
    delta = compare_medical_reports(report_a, report_b)
    assert "Improvement in WBC count" in delta
