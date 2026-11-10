# ComplaintAssist | Ankura AI Advisory Assessment Prototype

**Fictional-data staff-facing complaint triage, evidence retrieval and specialist handover application.**

## What works

- 30 original labelled fictional cases, 18 phrase-variation challenge cases, and six fictional policy documents (18 sections).
- Offline classification baseline: category, team, priority and rationale; optional OpenAI structured-output classification AND constrained handover drafting.
- Rule-based evidence retrieval (BM25-inspired lexical ranking) with inspectable policy-section citations.
- Case-note chronology, required-field completeness checks, specialist handover drafts; optional source-constrained generative drafts with citation-ID checks.
- Human review with editable summary, explicit acknowledgement enforced in browser/API, approve/reject controls, SQLite persistence and audit events.
- Input redaction, basic suspicious-instruction warning and conservative manual review. Automated tests and reproducible evaluation.

**Important:** The default path is a transparent **rules-based prototype**, not an LLM. Optional OpenAI mode can provide structured triage and an evidence-constrained handover, but is not validated here without API access. This honest separation enables offline testing without an API key. The retrieval is lexical, not a vector database, and the audit trail is a local proof-of-concept, not tamper-evident production infrastructure.

## Recommended browser demo (no Streamlit required)

```bash
cd complaint_assist
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload
```

Visit **http://127.0.0.1:8000/** for the review dashboard. The browser interface uses the same API endpoints and can be checked with automated FastAPI integration tests. A real browser-based smoke test was not available in the build environment.

## Alternative Streamlit interface

Requires Python 3.10+.

```bash
cd complaint_assist
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Choose CASE-001, click **Analyse complaint**, inspect evidence and missing fields, edit the draft, tick confirmation and record approval/rejection. Switch cases to explore categories. The review is persisted to `data/reviews.sqlite3`.

**Optional LLM mode:** Set `OPENAI_API_KEY` in your shell environment (do not place your secret in screenshots or committed files), select OpenAI mode from the sidebar. If API access fails, it reverts to deterministic rules and discloses this limitation. Both optional model calls receive redacted text, but regex may miss sensitive information; use synthetic data only. Optional LLM mode was not run during this validation because an API key and OpenAI package were unavailable in the build environment.

## Optional REST API

```bash
uvicorn api:app --reload
```

Browse `http://127.0.0.1:8000/docs`, or POST:

```json
{"case_id":"CASE-001","use_llm":false}
```

to `/analyse`; POST review decisions to `/review/CASE-001`.

## Evaluation and unit tests

```bash
python evaluate.py
python -m pytest -q
python evaluate_challenge.py
```

Results are written to `results/evaluation.json` and `results/challenge_evaluation.json`. Baseline results: 27/30 (90%) accuracy on the original templated cases; 7/18 (38.9%) accuracy on the separately written challenge cases. The labelled policy section appeared among the top four retrieved passages for 8/18 (44.4%) challenge cases. All 12 automated tests pass. These synthetic results show brittleness; they do not establish performance in actual banking operations. Accuracy is measured against authored labels for the synthetic cases. Citation-validity checks ensure IDs refer to retrieved passages, **not** that citations support particular claims. The dataset is heavily templated and not representative of real bank complaints. Do not claim time savings without a controlled study.

## Architecture

1. Staff opens case → raw complaint and notes.
2. Regex-based redaction → cautious prompt-injection warning.
3. Triage → deterministic baseline or optional OpenAI structured-output model, validated through Pydantic.
4. Retrieval → policy candidates with stable IDs and versions.
5. Handover → summary (original redacted complaint), chronology, checklist-driven missing fields, next steps and citations.
6. Human review → edit and explicit final approval/rejection.
7. Audit → draft and reviewer decisions stored locally in SQLite.

## Suggested assessor demo (3 minutes)

- Select CASE-001: payment dispute, incomplete evidence, policy source and human review.
- Select CASE-005: ongoing suspected fraud, higher urgency suggestion.
- Select CASE-007: account access, routing to Digital Support.
- Run `python evaluate.py` and show labelled-case metrics.
- Show approved handover and SQLite-backed audit record.

## Controls, limitations and engineering tradeoffs

- Only synthetic cases and fictional policies; no real banking systems, external customer data or payment actions.
- Review required on **every** recommendation, not just low-confidence cases.
- Local database does not have role-based access or cryptographic audit integrity.
- The simple PII redactor only targets common email/phone/card patterns; it is not comprehensive privacy protection.
- Regex injection checks are indicators, not sufficient security protections; the system makes no financial decisions.
- Evidence search is simple and interpretable; compare against BM25/vector retrieval before future production use.
- Offline rules are deterministic but brittle; optional LLM output can be wrong and must be evaluated separately.
- Need authentication, access control, robust monitoring, secure secrets, comprehensive evaluations, fairness/privacy assessment, bank-policy validation and staff trials before production.

## AI tools and their assessment

- LangGraph and LLM structured outputs were considered from earlier projects; the supplied demo intentionally uses explicit Python orchestration because the workflow has fixed steps and doesn't need autonomous decisions. Less orchestration complexity helps auditability.
- OpenAI `beta.chat.completions.parse` is optional for schema-constrained triage and handover drafting. The optional generated draft is bounded to retrieved citation IDs, with a disclosed template fallback. Advantage: handles varied natural language. Drawbacks: variable costs, external API dependencies, privacy risk and model errors.
- Rules mode provides a dependable, no-key baseline but handles only phrases anticipated by test authors.
- No AI tools were used to process real customer information. Never imply this is a deployed production bank system.

## Suggested scope for the five-page supporting document

1. Problem and business value; 2. Architecture and AI tools; 3. Testing and evidence; 4. Governance controls; 5. Workforce impact, limitations and trade-offs.

## Validation notes (10 November 2026)

- FastAPI `/`, `/health`, `/cases`, `/analyse` and review-confirmation paths were checked through HTTP and automated integration tests.
- Streamlit and the OpenAI SDK could not be installed in the validation environment because package network access was unavailable. No claim of a successful live Streamlit session or OpenAI model run is made.
- Playwright browser automation was not available because its Chromium binary was absent; browser UI remains for the assessor to inspect locally.
- Reviews are local demonstrations without authentication. Never publicly deploy with customer data or expose the API without access controls.
- The five-page PDF reports the harder challenge-set results prominently rather than presenting only the original template accuracy.


## NEW: free local AI through Ollama (Apple M2 / 8 GB RAM)

1. Install the macOS Ollama application from https://ollama.com/download and open it.
2. In a Terminal run `ollama pull qwen2.5:3b` (about 1.9 GB on disk).
3. Check `ollama list` and `curl http://127.0.0.1:11434/api/tags`.
4. In a separate Terminal, navigate to this `complaint_assist` folder and activate your Python venv.
5. Run `pip install -r requirements.txt` then `streamlit run app.py` or `uvicorn api:app --reload`.
6. Select **Ollama local AI (free)** in the UI and click **Analyse complaint**.
7. Confirm the classification mode is `LLM` and drafting method `LLM`; if they say `rules`, inspect the displayed fallback explanation.

This uses the local Ollama API at 127.0.0.1:11434 and does not use an OpenAI API key.
Set `OLLAMA_MODEL=qwen2.5:3b` optionally; leave it unset to use the default.
The model is not bundled with this repository. Tests mock model outputs; live local generation and accuracy must be tested on your Mac.
The assessors will need to install Ollama or see a locally hosted recording; keep the offline mode for a no-install demonstration.
Never expose the local Ollama port publicly. This prototype accepts only synthetic data.
