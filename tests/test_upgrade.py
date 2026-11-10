import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from api import app
from handover_ai import SuggestedDraft
from workflow import build_draft, cases
from storage import get_review
from schemas import ReviewInput
import pytest

client=TestClient(app)

def test_http_health_and_browser():
    assert client.get('/').status_code==200
    assert 'ComplaintAssist' in client.get('/').text
    assert client.get('/health').json()['status']=='ok'
    assert len(client.get('/cases').json()['cases'])==30

def test_http_analysis():
    result=client.post('/analyse',json={'case_id':'CASE-001','use_llm':False})
    assert result.status_code==200
    b=result.json()
    assert b['handover']['status']=='pending_review'
    assert b['drafting_method']=='rules'
    assert b['evidence']
    assert b['handover']['missing_information']

def test_missing_case():
    assert client.post('/analyse',json={'case_id':'CASE-999'}).status_code==404

def test_review_requires_explicit_confirmation():
    assert client.post('/review/CASE-001',json={'reviewer':'DEMO','decision':'approved',
           'edited_summary':'Verified synthetic complaint and evidence','confirmed':False}).status_code==400
    with pytest.raises(ValueError):
        from storage import save_review
        save_review('CASE-001',ReviewInput(reviewer='DEMO',decision='approved',
                    edited_summary='Verified synthetic complaint and evidence',confirmed=False))

def test_constrained_model_schema():
    d=SuggestedDraft(summary='This is a redacted synthetic complaint about card payments.',
       proposed_next_steps=['Verify original payment reference.'],policy_citations=['POL-002-S2.1'])
    assert len(d.policy_citations)==1


def test_ai_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    out=build_draft(cases()[0],use_llm=True)
    assert out['mode']=='rules' and out['drafting_method']=='rules'
    assert any('unavailable' in s.lower() for s in out['handover']['limitations'])
