"""Complaint -> privacy screening -> triage -> policy search -> draft -> human review.
LLM mode is optional. Rules mode is deterministic and entirely offline.
"""
import json, os, re
from pathlib import Path
from schemas import Handover, Triage
from triage import classify
from security import redact, injection_warning
from retrieval import retrieve,citation_ids_exist
from storage import get_review,record_draft
BASE=Path(__file__).parent
REQUIREMENTS={
 'payment_dispute':['transaction reference','transaction date','transaction amount'],
 'suspected_fraud':['transaction reference','transaction date','customer security contact'],
 'account_access':['account reference','last successful login'],
 'fees_charges':['fee reference','fee amount'],
 'service_quality':['date of contact','previous contact reference'],
 'other':['complaint description'],
}

def cases():
    return json.loads((BASE/'data/cases.json').read_text())

def find_case(case_id):
    return next((c for c in cases() if c['case_id']==case_id),None)

def extract_missing(case,category):
    present=set(case.get('available_fields',[]))
    return [name for name in REQUIREMENTS[category] if name not in present]

def build_draft(case, use_llm=False, save_audit=False, llm_provider="openai"):
    raw=case['complaint']+'\n'+'\n'.join(case.get('notes',[]))
    redacted, detected=redact(raw)
    flagged=injection_warning(raw)
    triage=classify(redacted)
    # LLM mode is optional. Only redacted data may be sent to a model.
    llm_error=None
    if use_llm and not flagged:
        try:
            if llm_provider == "ollama":
                from ollama_adapter import classify_local
                triage=classify_local(redacted)
            else:
                from ai_adapter import classify_llm
                triage=classify_llm(redacted)
        except Exception as exc:
            llm_error=f'LLM unavailable; rules baseline used ({type(exc).__name__}).'
    elif use_llm and flagged:
        llm_error='Suspicious instructions detected. Rules baseline used and human review required.'
    evidence=retrieve(redacted+' '+triage.category.replace('_',' ')+' specialist handover',k=4)
    # Notes are synthetic, but avoid presenting any unstated inferred facts as evidence.
    timeline=[redact(note)[0] for note in case.get('notes',[])]
    missing=extract_missing(case,triage.category)
    next_steps=['Verify the original complaint and case notes before any action.',
                f'Review relevant policy and route to {triage.team} if appropriate.']
    if missing:next_steps.append('Request missing information: '+', '.join(missing)+'.')
    else: next_steps.append('Confirm the evidence is sufficient for specialist review.')
    summary=redact(case['complaint'])[0]
    citations=[e['chunk_id'] for e in evidence]
    if not citation_ids_exist(citations,evidence):raise ValueError('Invalid evidence references')
    drafting_method='rules'
    # Optional LLM drafting is independently validated. On errors, retain the
    # clearly labelled offline draft; never claim LLM generation succeeded.
    if use_llm and not flagged:
        try:
            if llm_provider == "ollama":
                from ollama_adapter import draft_local
                generated=draft_local(summary,'\n'.join(timeline),triage,evidence,missing)
            else:
                from handover_ai import generate_grounded_draft
                generated=generate_grounded_draft(summary,'\n'.join(timeline),triage,evidence,missing)
            summary=generated.summary
            next_steps=generated.proposed_next_steps
            citations=generated.policy_citations
            drafting_method='llm'
        except Exception as exc:
            if llm_error: llm_error+=' '
            else: llm_error=''
            llm_error+=f'AI drafting unavailable; transparent template used ({type(exc).__name__}).'
    elif use_llm and flagged:
        drafting_method='rules'
    limitations=['No automatic redress or final complaint decision.',
                 'Retrieved passages are candidates; a reviewer must verify substantive support.',
                 'Rule-based baseline may misclassify complex or ambiguous complaints.']
    if llm_error:limitations.append(llm_error)
    if flagged:limitations.append('Suspicious instruction-like text detected; manual inspection required.')
    handover=Handover(case_id=case['case_id'],summary=summary,timeline=timeline,
       team=triage.team,category=triage.category,priority=triage.priority,
       missing_information=missing,proposed_next_steps=next_steps,
       policy_citations=citations,limitations=limitations)
    existing=get_review(case['case_id'])
    if existing:handover.status=existing['status']
    if save_audit:record_draft(case['case_id'],triage.category,triage.team,citations)
    return {'handover':handover.model_dump(),'triage':triage.model_dump(),
       'evidence':evidence,'privacy_flags':detected,'injection_warning':flagged,
       'review':existing,'mode':'llm' if triage.method=='llm' else 'rules',
       'drafting_method':drafting_method}
