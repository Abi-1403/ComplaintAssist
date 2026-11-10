"""Validated structures shared across workflow and API."""
from typing import Literal
from pydantic import BaseModel, Field

Category = Literal['payment_dispute','suspected_fraud','account_access','fees_charges','service_quality','other']
Team = Literal['Payments','Fraud','Digital Support','Account Services','Complaints','General Support']
Priority = Literal['low','medium','high','critical']

class Triage(BaseModel):
    category: Category
    team: Team
    priority: Priority
    rationale: str
    requires_human_review: bool = True
    method: Literal['rules','llm'] = 'rules'

class Evidence(BaseModel):
    chunk_id: str
    policy_id: str
    title: str
    section: str
    version: str
    text: str
    score: float = 0

class Handover(BaseModel):
    case_id: str
    summary: str
    timeline: list[str]
    team: Team
    category: Category
    priority: Priority
    missing_information: list[str]
    proposed_next_steps: list[str]
    policy_citations: list[str]
    limitations: list[str]
    status: Literal['pending_review','approved','rejected'] = 'pending_review'

class ReviewInput(BaseModel):
    reviewer: str = Field(min_length=2, max_length=80)
    decision: Literal['approved','rejected']
    edited_summary: str = Field(min_length=12, max_length=5000)
    notes: str = Field(default='', max_length=2000)
    confirmed: bool = False
