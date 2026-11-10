"""Streamlit staff dashboard; run with `streamlit run app.py`."""
import json, os
import streamlit as st
from workflow import cases, build_draft
from schemas import ReviewInput
from storage import save_review,get_audit,get_review,init

st.set_page_config(page_title='ComplaintAssist | AI Advisory POC',page_icon='📋',layout='wide')
init()
st.title('ComplaintAssist')
st.caption('AI-assisted complaint triage, policy evidence and specialist handovers | Fictional banking prototype')
with st.sidebar:
    st.subheader('Prototype settings')
    mode=st.radio('Analysis mode',['Offline rules baseline','Ollama local AI (free)','OpenAI structured triage'],index=0)
    if mode.startswith('OpenAI') and not os.getenv('OPENAI_API_KEY'):
        st.warning('No OPENAI_API_KEY configured. The pipeline will fall back to offline rules.')
    if mode.startswith('Ollama'):
        st.caption('Local model: '+os.getenv('OLLAMA_MODEL','qwen2.5:3b')+' · No OpenAI key required')
    st.info('No real customer data. No compensation or account action is automated.')
    st.divider()
    st.markdown('**Staff workflow**')
    st.write('1. Select case  2. Analyse  3. Verify sources  4. Edit and approve  5. Audit')
all_cases=cases()
labels={c['case_id']:c['case_id']+' · '+c['complaint'][:64] for c in all_cases}
chosen=st.selectbox('Select synthetic complaint',list(labels),format_func=lambda c:labels[c])
case=next(c for c in all_cases if c['case_id']==chosen)
left,right=st.columns([1,1.3])
with left:
    st.subheader('Customer complaint')
    st.write(case['complaint'])
    st.subheader('Existing case notes')
    for n in case['notes']:st.markdown('- '+n)
    st.caption('Fictional case data. Source fields intentionally incomplete in some examples.')
with right:
    st.subheader('AI-assisted analysis')
    if st.button('Analyse complaint',type='primary',use_container_width=True):
        st.session_state['analysis']=build_draft(case,use_llm=mode!='Offline rules baseline',llm_provider='ollama' if mode.startswith('Ollama') else 'openai',save_audit=True)
        st.session_state['case_id']=chosen
    if st.session_state.get('case_id')!=chosen:
        st.info('Select Analyse complaint to create a draft for this case.')
    else:
        result=st.session_state['analysis']
        triage=result['triage']; handover=result['handover']
        c1,c2,c3=st.columns(3)
        c1.metric('Suggested team',triage['team'])
        c2.metric('Priority',triage['priority'].title())
        c3.metric('Triage mode',result['mode'].upper())
        st.caption('Handover drafting: '+result.get('drafting_method','rules').upper()+' | All outputs require human review')
        st.write('**Category:**',triage['category'].replace('_',' ').title())
        st.write('**Privacy flags:**',', '.join(result['privacy_flags']) or 'None detected')
        if result['injection_warning']:st.error('Suspicious instruction-like input flagged; manual review required.')
        if handover['missing_information']:st.warning('Missing: '+', '.join(handover['missing_information']))
        else:st.success('No missing fields detected by this demo checklist.')
        st.markdown('### Candidate policy evidence')
        for e in result['evidence']:
            with st.expander(f"{e['chunk_id']} · {e['title']} (v{e['version']})"):
                st.write(e['text'])
                st.caption('Retrieved evidence candidate; verify applicability before approval.')
        st.markdown('### Handover draft')
        st.write('**Draft summary:**', handover['summary'])
        st.write('**Timeline:**')
        for note in handover['timeline']: st.markdown('- '+note)
        st.write('**Proposed next steps**')
        for step in handover['proposed_next_steps']:st.markdown('- '+step)
        st.caption('Sources: '+', '.join(handover['policy_citations']))
        with st.form(f'review_{chosen}'):
            edited=st.text_area('Editable complaint summary',value=handover['summary'],height=110)
            reviewer=st.text_input('Reviewer name (demo identifier)',value='DEMO-HANDLER-01')
            notes=st.text_area('Review notes',placeholder='Explain any corrections or unresolved evidence gaps')
            decision=st.radio('Decision',['approved','rejected'],horizontal=True,format_func=str.title)
            agree=st.checkbox('I verified the case, evidence and handover details; this is a human decision.')
            submitted=st.form_submit_button('Record human decision',disabled=bool(get_review(chosen) and get_review(chosen)['status']=='approved'))
            if submitted:
                if not agree:st.error('Confirm human verification before finalising.')
                else:
                    try:
                        review=ReviewInput(reviewer=reviewer,decision=decision,edited_summary=edited,notes=notes,confirmed=True)
                        save_review(chosen,review)
                        st.success('Human decision saved. View the audit history below.')
                    except Exception as exc:st.error(str(exc))
        existing=get_review(chosen)
        if existing:st.info(f"Current human review: {existing['status']} · {existing['reviewer']}")
        with st.expander('Workflow limitations and safeguards'):
            for limitation in handover['limitations']:st.markdown('- '+limitation)
        with st.expander('Audit trail'):
            audit=get_audit(chosen)
            if audit:st.dataframe([{'when':a['created_at'],'event':a['event'],'details':a['details_json']} for a in audit],use_container_width=True,hide_index=True)
            else:st.write('No events recorded yet.')
        st.download_button('Export draft JSON',json.dumps(result,indent=2),file_name=f'{chosen}_analysis.json',mime='application/json')
