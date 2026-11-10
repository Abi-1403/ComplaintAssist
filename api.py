"""Optional FastAPI routes for integration or test clients."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field
from workflow import find_case,build_draft,cases
from schemas import ReviewInput
from storage import save_review, get_review, get_audit
app=FastAPI(title='ComplaintAssist demo API',version='1.0')
class AnalyseInput(BaseModel):
    case_id: str
    use_llm: bool=False
    llm_provider: str="openai"
@app.get('/')
def browser_demo(): return FileResponse(Path(__file__).parent/'web/index.html')
@app.get('/cases')
def list_cases(): return {'cases':cases()}
@app.get('/health')
def health():return {'status':'ok','data':'synthetic'}
@app.post('/analyse')
def analyse(payload:AnalyseInput):
    case=find_case(payload.case_id)
    if not case:raise HTTPException(status_code=404,detail='Case not found')
    if payload.llm_provider not in ('openai', 'ollama'):
        raise HTTPException(status_code=422,detail='Unsupported model provider')
    return build_draft(case,use_llm=payload.use_llm,llm_provider=payload.llm_provider,save_audit=True)
@app.post('/review/{case_id}')
def review_case(case_id:str,body:ReviewInput):
    if not find_case(case_id):raise HTTPException(status_code=404,detail='Case not found')
    if not body.confirmed:raise HTTPException(status_code=400,detail='Explicit human verification confirmation required')
    try:save_review(case_id,body)
    except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc))
    return {'review':get_review(case_id)}
@app.get('/audit/{case_id}')
def audit(case_id:str):return {'events':get_audit(case_id)}
