"""Auditable, offline BM25-lite lexical search over versioned policy sections."""
import json, re, math
from pathlib import Path
BASE=Path(__file__).parent
SYNONYMS={'fraud':'unauthorised scam suspicious card transaction','payment':'disputed duplicate charge transfer card','access':'password login account authentication','fee':'charge interest overdraft','handover':'specialist evidence summary missing reference','complaint':'review escalation service case'}
def tokens(text):
    return re.findall(r'[a-z0-9]+',text.lower())

def load_policies():
    return json.loads((BASE/'data/policies.json').read_text())

def retrieve(query, k=3, docs=None):
    docs=docs if docs is not None else load_policies()
    q=tokens(query)
    # Expand common banking terminology, while preserving the original query.
    q+= [w for word in list(q) for w in tokens(SYNONYMS.get(word,''))]
    if not q:return []
    contents=[tokens(d['title']+' '+d['section']+' '+d['text']) for d in docs]
    avglen=sum(map(len,contents))/max(1,len(contents))
    scored=[]
    for d,words in zip(docs,contents):
        score=0.0
        for term in set(q):
            tf=words.count(term)
            if not tf: continue
            df=sum(term in other for other in contents)
            idf=math.log(1+(len(docs)-df+0.5)/(df+0.5))
            score += idf*tf*2.2/(tf+1.2*(0.25+0.75*len(words)/max(avglen,1)))
        if score>0:scored.append({**d,'score':round(score,3)})
    return sorted(scored,key=lambda x:(-x['score'],x['chunk_id']))[:k]

def citation_ids_exist(ids, evidence):
    valid={e['chunk_id'] for e in evidence}
    return all(i in valid for i in ids)
