from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from pathlib import Path
import json
B=Path(__file__).parent
out=B/'ComplaintAssist_Assessment_Brief.pdf'
eval=json.loads((B/'results/evaluation.json').read_text())
W,H=595,842
C=canvas.Canvas(str(out),pagesize=(W,H)); C.setTitle('ComplaintAssist | Five-page prototype assessment brief')
NAVY=HexColor('#192B48');PURPLE=HexColor('#6344AA');MUTED=HexColor('#56667B');GRAY=HexColor('#EDF0F6')
def rect(x,y,w,h,fill=GRAY):
 C.setFillColor(fill);C.roundRect(x,y,w,h,9,fill=1,stroke=0)
def text(x,y,string,size=10,color=NAVY,font='Helvetica'):
 C.setFillColor(color);C.setFont(font,size);C.drawString(x,y,string)
def para(s,x,y,width=487,size=10,leading=15,color=NAVY):
 for line in simpleSplit(s,'Helvetica',size,width):
  text(x,y,line,size,color);y-=leading
 return y-9
def section(title,y):
 text(52,y,title,13,PURPLE,'Helvetica-Bold');return y-23
def bullet(s,y):
 text(57,y,'-',11,PURPLE,'Helvetica-Bold');return para(s,72,y,467,10,15)
def header(num,title,kicker):
 rect(0,H-99,W,99,NAVY)
 text(50,H-42,'COMPLAINTASSIST  /  ANKURA ASSESSMENT',10,HexColor('#DFD7FF'),'Helvetica-Bold')
 text(50,H-75,title,22,HexColor('#FFFFFF'),'Helvetica-Bold')
 text(51,H-120,kicker,10,MUTED)
 C.setStrokeColor(HexColor('#D5DBE4')); C.line(50,52,W-50,52)
 text(50,35,'Fictional data only   |   Prototype, not a production banking system',9,MUTED)
 text(W-80,35,f'{num} / 5',9,PURPLE,'Helvetica-Bold')
def finish():C.showPage()
header(1,'Client problem and value','Scenario 1: Banking complaint handling')
y=685;y=section('Client challenge',y)
y=para('The fictional bank faces a growing complaint backlog, slow searches across customer notes and policy documents, and incomplete handovers to specialist teams. Automation must preserve confidentiality, auditability and human accountability.',52,y)
y=section('Proposed intervention',y)
y=para('ComplaintAssist is a staff-facing decision-support prototype, not a customer-facing chatbot or an automated redress engine. It provides suggested triage, policy evidence, missing-field warnings and an editable specialist handover that cannot be approved without a human review.',52,y)
y=section('Potential business value',y)
for s in ['Reduce time spent searching notes and reference policies (hypothesis, not yet measured).','Improve handover completeness by checking category-specific required information.','Reduce misrouting through consistent classification, while retaining human override.','Improve traceability through versioned source IDs and recorded employee decisions.']:y=bullet(s,y)
y=section('Boundaries and assumptions',y)
y=para('The demo uses 30 main synthetic cases, 18 challenge cases, 18 sections from six invented bank policies and local SQLite review records. Policy rules and routing labels are fictional. It does not connect to bank systems, settle complaints, contact customers or issue refunds.',52,y)
finish()
header(2,'How the prototype works','Technical architecture and tools')
y=681;y=section('Data flow',y)
for s in ['1   Staff selects a fictional complaint and its case notes.','2   Input is checked for common PII patterns and suspicious instruction-like text.','3   Rules-based triage suggests issue category, urgency and specialist team.','4   Lexical retrieval ranks policy sections and exposes versioned citations.','5   A structured handover includes chronology, missing fields and next steps.','6   Staff inspect evidence, edit the summary and explicitly approve or reject.','7   A SQLite audit records generation and human review events.']:y=bullet(s,y)
y-=2;y=section('Tools and trade-offs',y)
for s in ['Python + Pydantic: explicit data types and deterministic validation.','FastAPI + plain HTML browser demo; optional Streamlit interface. Both require a local server.','SQLite: persistent local audit trail; not tamper-evident or multi-user secure.','BM25-inspired lexical search: interpretable offline retrieval; no semantic embedding search.','Optional OpenAI structured triage and evidence-constrained drafting: untested without API access; invalid drafts fall back to templates.']:y=bullet(s,y)
y=section('Assessment of AI tool use',y)
y=para('Default is offline rules and template drafting. Optional OpenAI mode provides structured triage and source-constrained handover drafting, validated against retrieved citation IDs. The model was not evaluated in this environment; fallback is explicit. Output remains a human-reviewed draft.',52,y)
finish()
header(3,'Testing, evidence and limitations','Actual local evaluation; not client impact')
y=681;y=section('Executed tests',y)
rect(50,y-101,495,90)
text(70,y-35,'30 + 18',23,PURPLE,'Helvetica-Bold');text(226,y-35,'38.9%',26,PURPLE,'Helvetica-Bold');text(398,y-35,'12/12',26,PURPLE,'Helvetica-Bold')
text(70,y-56,'Template + challenge',10,MUTED);text(226,y-56,'Challenge accuracy',10,MUTED);text(398,y-56,'Tests passed',10,MUTED)
y-=129
for s in ['Original template set: 27/30 correct categories (90%); this is a weak generalisation test.','Phrase-variation challenge set: 7/18 correct categories (38.9%), revealing brittle rules.','Challenge retrieval: 8/18 labelled policy sections appeared in the top four (44.4%).','Original set: 30/30 cases required review; 30/30 citations had valid IDs, not proven support.','12 tests passed, including API routes, confirmation checks and safe AI fallback.']:y=bullet(s,y)
y=section('Limitations of these measurements',y)
for s in ['Both sets are small and authored for this project; the second set deliberately varies wording.','No real employee handling-time measurements, cost savings or financial ROI have been established.','Optional OpenAI triage and handover generation are untested without an API key.','Recall@4 tests retrieving a labelled reference, not claim-level citation support.']:y=bullet(s,y)
y=section('Next evaluation stage',y)
y=para('Before piloting: collect independently authored blind cases, improve routing/retrieval, verify claim support, assess PII leakage and time trained handlers on manual versus assisted workflows.',52,y)
finish()
header(4,'Governance and human controls','Responsible AI and operational safeguards')
y=681;y=section('Controls implemented in the demonstration',y)
for s in ['Synthetic data only: no genuine customer information is required.','Regex redaction for common email, telephone and payment-card patterns before optional LLM triage.','A limited pattern-based warning for instruction-like input, with human inspection required.','Pydantic validation of category, team, priority and handover structure.','Every handover is a draft until an employee explicitly confirms review and records approval.','Review confirmation, changes and decisions are recorded in local SQLite; approvals lock further edits.']:y=bullet(s,y)
y=section('Residual risk and required production controls',y)
for s in ['Regex redaction and pattern matching are incomplete; data-loss-prevention checks need broader coverage.','Policy retrieval can return weak or irrelevant passages; verify evidence applicability manually.','No authentication, role-based access, immutable audit or enterprise secrets management.','No live banking integration, approved policy governance, model monitoring or incident response.','Business rules are hypothetical; compliance requirements need review by bank policy and legal teams.']:y=bullet(s,y)
y=section('Decision rights',y)
y=para('The system proposes information. A bank employee verifies facts, priorities, evidence, omissions and final handover content. Specialist decisions, compensation, fraud investigations and account actions remain entirely outside the prototype.',52,y)
finish()
header(5,'Workforce impact and next steps','Adoption, assumptions and recommendation')
y=681;y=section('How the workflow changes',y)
for s in ['Today (illustrative): a handler reads complaint notes, searches multiple documents, prepares a summary and sends it to a specialist.','Proposed: the handler starts with an AI-assisted triage and draft, checks citations, corrects omissions, and approves the handover.','Specialists receive more structured inputs; managers monitor handover quality and override patterns.','Staff require training in verification, data protection, handling uncertainty and escalating incorrect AI recommendations.']:y=bullet(s,y)
y=section('Assumptions and trade-offs',y)
for s in ['Assumes structured case notes and approved policy sources can be made available in a future bank environment.','Deterministic baseline maximises reproducibility, but misses language variation; LLM triage may improve coverage with additional complexity.','Local SQLite keeps the demo easy to open, but limits multi-user security and deployment readiness.','Mandatory human review adds effort but makes accountability explicit.']:y=bullet(s,y)
y=section('Practical next steps',y)
for s in ['Evaluate against independently written, held-out examples and difficult edge cases.','Trial with complaint handlers to measure actual time, completeness and override rates.','Harden privacy, authentication, permissions, audit integrity and source governance.','Conduct formal business-risk, accessibility and compliance reviews before considering a pilot.']:y=bullet(s,y)
y=section('Recommendation',y)
y=para('Treat ComplaintAssist as a testable proof of concept for staff decision support. Proceed toward a controlled pilot only if independent evaluation and staff trials demonstrate measurable benefits without unacceptable safety, privacy or operational trade-offs.',52,y)
finish();C.save()
print(out)
