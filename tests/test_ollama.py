from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ollama_adapter
from workflow import build_draft, cases

def test_local_triage_enforces_team_and_human_review(monkeypatch):
    def fake(*args):
        return {'category':'payment_dispute','team':'Fraud','priority':'high',
                'rationale':'Disputed duplicate charge','requires_human_review':False,'method':'llm'}
    monkeypatch.setattr(ollama_adapter,'_ask_ollama',fake)
    out=ollama_adapter.classify_local('I was charged twice')
    assert out.team=='Payments' and out.requires_human_review is True

def test_local_draft_rejects_fabricated_citation(monkeypatch):
    from schemas import Triage
    def fake(*args):
        return {'summary':'Customer disputes a payment and needs a human review.',
                'proposed_next_steps':['Check supporting records.'],
                'policy_citations':['FAKE-SECTION']}
    monkeypatch.setattr(ollama_adapter,'_ask_ollama',fake)
    try:
        ollama_adapter.draft_local('A duplicate payment','Notes',Triage(category='payment_dispute',team='Payments',priority='medium',rationale='Duplicate'),
                                 [{'chunk_id':'POL-001-S1','text':'Evidence'}],['transaction reference'])
    except ValueError as exc:
        assert 'citation' in str(exc)
    else:
        raise AssertionError('Fabricated citation was accepted')

def test_full_local_flow_with_mock(monkeypatch):
    from handover_ai import SuggestedDraft
    from schemas import Triage
    monkeypatch.setattr(ollama_adapter,'classify_local', lambda text:Triage(category='payment_dispute',team='Payments',priority='medium',rationale='Payment',method='llm'))
    def draft(*args):
        evidence=args[3]
        return SuggestedDraft(summary='Customer reported a disputed duplicate charge in the account.',
                              proposed_next_steps=['Review transaction evidence.'],
                              policy_citations=[evidence[0]['chunk_id']])
    monkeypatch.setattr(ollama_adapter,'draft_local', draft)
    out=build_draft(cases()[0],use_llm=True,llm_provider='ollama')
    assert out['mode']=='llm' and out['drafting_method']=='llm'
