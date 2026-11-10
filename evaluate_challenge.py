"""Separately authored phrase-variation challenge set. Not an independent population sample."""
import json
from pathlib import Path
from triage import classify
from retrieval import retrieve
from security import redact
B=Path(__file__).parent

def run():
    rows=json.loads((B/'evaluation/challenge_cases.json').read_text())
    details=[]
    for r in rows:
        sanitized,_=redact(r['text'])
        p=classify(sanitized)
        evidence=retrieve(sanitized+' '+p.category.replace('_',' ')+' specialist handover',k=4)
        ids=[x['chunk_id'] for x in evidence]
        details.append({'id':r['id'],'expected':r['category'],'predicted':p.category,
                        'category_correct':p.category==r['category'],
                        'expected_policy':r['policy'],'retrieved_policy_ids':ids,
                        'policy_recall_at_4':r['policy'] in ids})
    cats=sorted(set(r['category'] for r in rows))
    by_cat={}
    for c in cats:
        subset=[x for x in details if x['expected']==c]
        tp=sum(x['category_correct'] for x in subset)
        pred=sum(x['predicted']==c for x in details)
        by_cat[c]={'support':len(subset),'precision':round(tp/pred,3) if pred else 0,
                   'recall':round(tp/len(subset),3)}
    result={'dataset':'18 separately authored synthetic phrase-variation challenge cases',
            'mode':'offline_rules_baseline','n_cases':len(details),
            'category_accuracy':round(sum(x['category_correct'] for x in details)/len(details),3),
            'expected_policy_recall_at_4':round(sum(x['policy_recall_at_4'] for x in details)/len(details),3),
            'per_category':by_cat,'details':details,
            'limitations':['Challenge cases were authored for this project, not sampled from banking operations.',
            'Expected-policy Recall@4 checks retrieval of one labelled reference; it is not claim-level citation support.',
            'Policy references are fictional; results do not establish regulatory adequacy.',
            'Optional OpenAI mode not measured unless separately run with API access.']}
    (B/'results/challenge_evaluation.json').write_text(json.dumps(result,indent=2))
    return result
if __name__=='__main__':
    result=run()
    print(json.dumps({k:v for k,v in result.items() if k!='details'},indent=2))
