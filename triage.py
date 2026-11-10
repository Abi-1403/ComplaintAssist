"""Transparent rules baseline. Optional LLM is used for extraction, not final routing authority."""
import re
from schemas import Triage
RULES = [
 ('suspected_fraud','Fraud',r'fraud|scam|unauthori[sz]ed|stolen|suspicious transaction|not mine|identity theft'),
 ('payment_dispute','Payments',r'double charg|charged twice|duplicate|disput(?:e|ed)|chargeback|payment revers|card payment|wrong transfer|transfer missing'),
 ('account_access','Digital Support',r'log ?in|locked out|password|access my account|two.factor|app crashes|cannot sign in'),
 ('fees_charges','Account Services',r'overdraft|fee|charges|interest rate|monthly charge|penalty'),
 ('service_quality','Complaints',r'rude|waited|no response|poor service|ignored|delayed response|unhelpful'),
]
HIGH = re.compile(r'fraud|scam|unauthori[sz]ed|stolen|vulnerab|financial hardship|urgent|today|cannot access money',re.I)
CRITICAL = re.compile(r'active fraud|ongoing fraud|immediate danger|threat to life',re.I)

def classify(text: str) -> Triage:
    s=text.lower()
    for cat,team,expr in RULES:
        if re.search(expr,s): break
    else: cat,team='other','General Support'
    priority = 'critical' if CRITICAL.search(text) else 'high' if HIGH.search(text) else 'medium'
    return Triage(category=cat,team=team,priority=priority,
      rationale=f'Rules matched the {cat.replace("_"," ")} category; staff must verify suggested routing.',
      requires_human_review=True,method='rules')
