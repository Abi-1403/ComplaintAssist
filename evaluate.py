"""Reproducible synthetic classification benchmark and case completeness checks."""
import json
from pathlib import Path
from workflow import cases,build_draft
from triage import classify
from retrieval import citation_ids_exist
B=Path(__file__).parent

def evaluate():
    dataset=cases(); n=len(dataset)
    correct=0; cited=0; incomplete=0; review_required=0
    per=[]
    for case in dataset:
        result=build_draft(case)
        triage=result['triage']; handover=result['handover']
        good=triage['category']==case['expected_category']
        correct+=good
        cited+=citation_ids_exist(handover['policy_citations'],result['evidence']) and bool(result['evidence'])
        incomplete+=bool(handover['missing_information'])
        review_required+=triage['requires_human_review']
        per.append({'case_id':case['case_id'],'expected':case['expected_category'],'predicted':triage['category'],'correct':good})
    out={'mode':'offline_rules_baseline','dataset':'30 labelled synthetic template cases',
       'n_cases':n,'classification_accuracy':round(correct/n,3),
       'citation_id_validity_rate':round(cited/n,3),
       'cases_with_missing_fields':incomplete,'human_review_flag_rate':round(review_required/n,3),
       'important_limitations':['Template-derived cases overestimate generalisation to real complaints.',
         'Citation ID validity only tests existence, not whether the passage supports the claim.',
         'No real staff time saving or regulatory compliance demonstrated.'],
       'per_case':per}
    (B/'results'/'evaluation.json').write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':
    result=evaluate()
    print(json.dumps({k:v for k,v in result.items() if k!='per_case'},indent=2))
