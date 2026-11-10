# ComplaintAssist | Ankura Digital AI Advisory Interview Exercise

**Scenario 1: Banking | Complaint handling**  
**Candidate:** Abiya Thangamuthu

ComplaintAssist is a staff-facing proof of concept for a **fictional bank**. It assists with complaint triage, retrieval of policy evidence, missing-information checks and specialist handover drafting. Staff must review and approve or reject handovers. It **does not** make final complaint, compensation or payment decisions.

All complaints, case notes and policies in the repository are fictional or synthetic.

## What the prototype demonstrates

- **Local LLM triage:** Qwen2.5 3B through Ollama suggests complaint categories and priorities. Category-to-team routing is enforced by a fixed mapping; an offline rules baseline is also available.
- **Policy retrieval:** BM25-inspired **lexical retrieval** ranks passages from six fictional policy documents, returning inspectable section IDs. This is not embedding-based vector search.
- **Structured handovers:** AI-assisted drafts summarise case information, identify missing required fields and reference retrieved evidence. Pydantic validates output structure and permitted citation IDs; this does **not** prove that every citation supports a claim.
- **Human-in-the-loop review:** Staff can inspect evidence, edit draft summaries, approve or reject them, and explicitly acknowledge human responsibility.
- **Audit trail:** Draft-generation and review events are stored in a local SQLite database.
- **Safeguards:** Basic input redaction, suspicious-instruction checks, human approval and offline fallback. These controls are proof-of-concept measures rather than production security guarantees.

## Run locally (Mac / Linux)

Prerequisites: Python 3.11+; Ollama for local AI mode.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To use local AI, install Ollama from https://ollama.com/download, open it, then run:

```bash
ollama pull qwen2.5:3b
ollama list
```

Launch the Streamlit app:

```bash
streamlit run app.py
```

Open the localhost address shown in the terminal. Select **Ollama local AI (free)** in the sidebar, choose a synthetic case and click **Analyse complaint**. Confirm the triage and handover modes report **LLM**, not **rules**, if you want to test live local generation. If Ollama is unavailable, choose **Offline rules baseline** to explore the workflow without a model download.

Alternative FastAPI interface:

```bash
uvicorn api:app --reload
```

Then open http://127.0.0.1:8000/ (API documentation: http://127.0.0.1:8000/docs).

**No OpenAI API key or paid service is required for Ollama or offline mode.** The Ollama model weights are not bundled with the repository.

## Suggested assessor walkthrough

1. Select **CASE-001** (disputed card charge); run analysis and inspect the category, missing information and policy evidence.
2. Read the generated handover and verify retrieved policy passages against it.
3. Edit the summary and record an **Approved** decision with reviewer acknowledgement.
4. Select **CASE-002**; record a **Rejected** decision and explain the unresolved evidence gap.
5. Expand **Audit trail** to see the separate draft and review events.

## Testing and evaluation

```bash
python -m pytest -q
python evaluate.py
python evaluate_challenge.py
python evaluate_ollama.py
```

The last command requires Ollama with `qwen2.5:3b` available locally. It writes `results/ollama_challenge_evaluation.json` and `.csv`.

**Observed on 10 November 2026:**

| Metric, 18 synthetic challenge complaints | Offline rules baseline | Ollama Qwen2.5 3B |
|---|---:|---:|
| Classification accuracy | 7/18 (38.9%) | **15/18 (83.3%)** |
| Expected policy present among top four retrieved passages | 8/18 (44.4%) | **13/18 (72.2%)** |

- Ollama model calls completed: **18/18**.
- Automated software tests: **15 passed**, as reported by a local `pytest` run.
- Live local UI checks: demonstrated AI triage/drafting, human approval, human rejection and audit-history entries.
- Manual policy review of one example found useful evidence alongside a less-directly relevant passage.

These are **small synthetic-set results**, not estimates of accuracy or time savings in real banking operations. Individual misclassification and retrieval-failure cases have not yet been fully analysed. The expected-policy metric measures retrieval presence, not semantic citation correctness. No staff productivity study has been conducted.

## Design choices and limitations

The fixed, auditable workflow uses Python orchestration, Streamlit/FastAPI, Pydantic, Ollama, lexical document retrieval and SQLite. It is **not** a production banking service, a full autonomous multi-agent platform or a vector-embedding RAG system.

Further work before real-world deployment would include identity and access controls, robust private-data handling, secure persistent storage and audit integrity, independent citation-grounding checks, fairness tests, broader labelled-case evaluations, policy-owner validation, monitoring and user research with complaint handlers and specialists.

## Repository contents

- `app.py` — Streamlit staff interface
- `api.py`, `web/` — FastAPI and browser UI
- `workflow.py`, `triage.py`, `handover_ai.py`, `ollama_adapter.py` — orchestration, triage and optional local AI
- `retrieval.py`, `data/policies/` — fictional policy search
- `schemas.py`, `security.py`, `storage.py` — validation, safeguards and local audit persistence
- `evaluation/challenge_cases.json`, `evaluate*.py`, `results/` — benchmark data, scripts and outputs
- `tests/` — automated tests

**Security:** Never commit `.env`, API keys, `.venv/`, Python caches or the local `data/reviews.sqlite3` file. All sample content in version control should be fictional.
