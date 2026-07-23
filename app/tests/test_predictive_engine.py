import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai_pipeline.predictive_engine import (
    calculate_health_score,
    predict_readmission_risk,
    detect_early_disease_signals,
    predict_medication_adherence
)
from ai_pipeline.copilot_engine import auto_assign_icd10

@pytest.mark.asyncio
@patch("ai_pipeline.copilot_engine.client.chat.completions.create", new_callable=AsyncMock)
async def test_auto_assign_icd10(mock_create):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "E11.9"
    mock_create.return_value = mock_response

    result = await auto_assign_icd10("Type 2 Diabetes", "Patient reports increased thirst.")
    assert result == "E11.9"

@pytest.mark.asyncio
@patch("ai_pipeline.predictive_engine.client.chat.completions.create", new_callable=AsyncMock)
async def test_calculate_health_score(mock_create):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"score": 85, "reasoning": "Patient is stable."}'
    mock_create.return_value = mock_response

    result = await calculate_health_score({"diseases": ["Hypertension"]})
    assert result["score"] == 85
    assert "stable" in result["reasoning"]

@pytest.mark.asyncio
@patch("ai_pipeline.predictive_engine.client.chat.completions.create", new_callable=AsyncMock)
async def test_predict_readmission_risk(mock_create):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"risk_level": "Low", "reasoning": "No recent major surgeries."}'
    mock_create.return_value = mock_response

    result = await predict_readmission_risk({"procedures": []})
    assert result["risk_level"] == "Low"

@pytest.mark.asyncio
@patch("ai_pipeline.predictive_engine.client.chat.completions.create", new_callable=AsyncMock)
async def test_detect_early_disease_signals(mock_create):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"signals": ["Elevated blood sugar"], "reasoning": "Possible pre-diabetes."}'
    mock_create.return_value = mock_response

    result = await detect_early_disease_signals({"labs": [{"test": "Glucose", "value": 115}]})
    assert "Elevated blood sugar" in result["signals"]

@pytest.mark.asyncio
@patch("ai_pipeline.predictive_engine.client.chat.completions.create", new_callable=AsyncMock)
async def test_predict_medication_adherence(mock_create):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"adherence_risk": "High", "reasoning": "Complex regimen."}'
    mock_create.return_value = mock_response

    result = await predict_medication_adherence({"medications": ["Metformin", "Lisinopril", "Atorvastatin"]})
    assert result["adherence_risk"] == "High"
