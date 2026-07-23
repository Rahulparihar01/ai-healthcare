from ai_pipeline.copilot_engine import client
import json

async def calculate_health_score(patient_data: dict) -> dict:
    prompt = f"""
    You are an expert predictive health AI. 
    Based on the following patient data, calculate a personalized health score from 0 to 100.
    Output a JSON object with two keys: "score" (integer) and "reasoning" (string, short explanation).
    
    Patient Data:
    {json.dumps(patient_data)}
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=150,
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"score": -1, "reasoning": f"Prediction failed: {e}"}

async def predict_readmission_risk(patient_data: dict) -> dict:
    prompt = f"""
    You are an expert predictive health AI. 
    Assess the 30-day readmission risk based on the patient data.
    Output a JSON object with "risk_level" ("Low", "Medium", "High") and "reasoning".
    
    Patient Data:
    {json.dumps(patient_data)}
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=150,
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"risk_level": "Unknown", "reasoning": "Prediction failed."}

async def detect_early_disease_signals(patient_data: dict) -> dict:
    prompt = f"""
    You are an expert predictive health AI. 
    Scan the patient data (especially lab trends and symptoms) for early warning signs of chronic conditions.
    Output a JSON object with "signals" (list of strings) and "reasoning".
    
    Patient Data:
    {json.dumps(patient_data)}
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"signals": [], "reasoning": "Prediction failed."}

async def predict_medication_adherence(patient_data: dict) -> dict:
    prompt = f"""
    You are an expert predictive health AI. 
    Predict if the patient is likely to miss medication doses based on regimen complexity.
    Output a JSON object with "adherence_risk" ("Low", "Medium", "High") and "reasoning".
    
    Patient Data:
    {json.dumps(patient_data)}
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=150,
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"adherence_risk": "Unknown", "reasoning": "Prediction failed."}
