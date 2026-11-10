"""Generate deterministic, wholly fictional banking data and source-labelled policies."""
import json
from pathlib import Path
B=Path(__file__).parent/'data'
policies=[
('POL-001','Complaints Intake and Triage','1.0',[
 ('1.1','Record the original complaint, a unique case ID, the reported impact and any previous contact.'),
 ('1.2','Complaint priority must be reviewed by a handler. Cases alleging active fraud or immediate security risk require urgent specialist consideration.'),
 ('1.3','Do not assume a complaint is substantiated solely because an automated classifier marked it high priority.')]),
('POL-002','Disputed Payments Procedure','1.0',[
 ('2.1','For a disputed card payment, document the transaction date, transaction amount and transaction reference. Flag missing evidence in the handover.'),
 ('2.2','Potential duplicate charges are referred to Payments. A specialist checks bank records before determining whether an adjustment is appropriate.'),
 ('2.3','Do not promise a refund or assert that fraud occurred before investigation.')]),
('POL-003','Fraud Escalation Procedure','1.0',[
 ('3.1','Suspected fraud complaints must identify available transaction details and record whether a customer security contact has occurred.'),
 ('3.2','Cases alleging ongoing fraud or compromised credentials should be highlighted promptly for the Fraud team. The AI must not independently restrict accounts.'),
 ('3.3','Specialist staff decide the investigation and any account controls. Drafts must not present suspicion as confirmed fraud.')]),
('POL-004','Account Access Procedure','1.0',[
 ('4.1','For account access issues, capture an account reference, a description of the login problem, and the last successful login where available.'),
 ('4.2','Digital Support reviews password and authentication problems. Never request or record a customer password or one-time code in a complaint handover.')]),
('POL-005','Fees and Service Complaints','1.0',[
 ('5.1','Fees complaints should provide fee amount and fee reference; Account Services investigates the application of fees.'),
 ('5.2','Service complaints must describe the experience, date of contact and any previous contact reference if available.'),
 ('5.3','Complaint handlers should distinguish customer allegations from verified records and record conflicting information explicitly.')]),
('POL-006','Specialist Handover and Data Protection','1.0',[
 ('6.1','A specialist handover must include a factual summary, chronology, assigned team, evidence references, missing information and suggested next steps.'),
 ('6.2','All AI-generated handovers are drafts. An authorised employee must review, edit if needed and explicitly approve before finalisation.'),
 ('6.3','Do not insert sensitive personal information into external AI prompts. Reviewers must check evidence citations and retain a record of material edits.'),
 ('6.4','If evidence is incomplete or the AI output is uncertain, mark the case for human review rather than manufacture missing facts.')]),
]
rows=[]
for pid,title,version,sections in policies:
 for sec,body in sections:
  rows.append(dict(chunk_id=f'{pid}-S{sec}',policy_id=pid,title=title,version=version,section=sec,text=body))
(B/'policies.json').write_text(json.dumps(rows,indent=2))
for pid,title,version,sections in policies:
 (B/'policies'/f'{pid}.md').write_text(f'# {title}\n\nDocument: {pid} | Version: {version}\n\n'+'\n\n'.join(f'## Section {s}\n{t}' for s,t in sections))
templates=[
 ('payment_dispute','I was charged twice for a card payment of £85. The extra transaction is still showing.', ['Customer reported a duplicate card charge on 02 Nov 2026.','Agent requested transaction supporting documents.'], ['transaction amount','transaction date']),
 ('payment_dispute','My card payment of £120 was debited but the merchant says it failed.', ['Customer contacted helpline about disputed payment.','Transaction reference PAY-2026-004 was recorded.'],['transaction reference','transaction amount']),
 ('payment_dispute','My bank transfer went missing and has not reached the other account.', ['Customer supplied transaction date 01 Nov 2026.','Customer supplied amount £250.'],['transaction date','transaction amount']),
 ('suspected_fraud','There is an unauthorised £400 card transaction on my account.', ['Customer reported card transaction FRA-204.','No security callback completed.'],['transaction reference','transaction date']),
 ('suspected_fraud','I think an active fraud scam is happening right now, with more money leaving.', ['Customer reported urgent ongoing unauthorised activity.','Security contact completed with fictional customer.'],['customer security contact']),
 ('suspected_fraud','My card was stolen and someone used it yesterday.', ['Customer provided transaction date 03 Nov 2026.','Security contact was recorded.'],['transaction date','customer security contact']),
 ('account_access','I am locked out of the mobile banking app after resetting my password.', ['Customer reported repeated login errors.','Account reference ACC-208 is available.'],['account reference']),
 ('account_access','I cannot sign in because my two-factor login keeps failing.', ['Customer reported last successful login on 01 Nov 2026.'],['last successful login']),
 ('account_access','The banking app crashes whenever I log in.', ['Account reference ACC-204 provided.','Last successful login date recorded.'],['account reference','last successful login']),
 ('fees_charges','I was charged an overdraft fee of £35 that I do not recognise.', ['Fee amount £35 recorded.','Customer has not provided fee reference.'],['fee amount']),
 ('fees_charges','Why is there a monthly charge on my account when I thought it was free?', ['Fee reference FEE-020 provided.'],['fee reference']),
 ('fees_charges','The bank has taken interest and charges I do not understand.', ['Fee reference FEE-019 provided.','Fee amount £19 recorded.'],['fee reference','fee amount']),
 ('service_quality','A staff member was rude during my visit and I want to complain.', ['Visit date recorded as 02 Nov 2026.'],['date of contact']),
 ('service_quality','I waited over two weeks with no response to my previous complaint.', ['Previous contact reference C-221 recorded.'],['previous contact reference']),
 ('service_quality','I received poor service and the agent ignored my messages.', ['Contact date and prior ticket reference C-222 both available.'],['date of contact','previous contact reference']),
 ('other','I would like to provide feedback on the bank newsletter.', ['Customer submitted general feedback through the web form.'],['complaint description']),
]
cases=[]
for i in range(30):
 category,text,notes,fields=templates[i%len(templates)]
 if i>=len(templates):
  text=text.replace('my ','my ').replace('£85','£86')
  if i%3==0:fields=fields[:1]
 cases.append({'case_id':f'CASE-{i+1:03}', 'complaint':text,'notes':notes,
    'available_fields':fields,'expected_category':category,
    'fictional':True})
(B/'cases.json').write_text(json.dumps(cases,indent=2))
print(len(cases),'cases and',len(rows),'policy chunks generated')
