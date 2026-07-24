import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from ai_pipeline.summarizer import generate_clinical_summary

@patch("ai_pipeline.summarizer.wrap_openai", side_effect=lambda x: x)
@patch("ai_pipeline.summarizer.OpenAI")
def test_generate_clinical_summary_blood_test(mock_openai, mock_wrap):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Normal blood test."
    mock_client.chat.completions.create.return_value = mock_response

    summary = generate_clinical_summary("blood_test", "WBC: 6.0, RBC: 4.5")
    
    assert summary == "Normal blood test."
    
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert "blood test" in kwargs["messages"][0]["content"].lower()

@patch("ai_pipeline.summarizer.wrap_openai", side_effect=lambda x: x)
@patch("ai_pipeline.summarizer.OpenAI")
def test_generate_clinical_summary_unknown_type(mock_openai, mock_wrap):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Unknown summary."
    mock_client.chat.completions.create.return_value = mock_response

    summary = generate_clinical_summary("random_type", "Some text")
    
    assert summary == "Unknown summary."
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["messages"][0]["content"] == "You are a medical assistant. Summarize the following medical document."

@patch("ai_pipeline.summarizer.wrap_openai", side_effect=lambda x: x)
@patch("ai_pipeline.summarizer.OpenAI")
def test_generate_clinical_summary_exception(mock_openai, mock_wrap):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    summary = generate_clinical_summary("blood_test", "Some text")
    
    assert summary == "AI processing failed to generate a summary."
