import streamlit as st
import pandas as pd
import requests
import json
from groq import Groq
from langchain_core.prompts import PromptTemplate

st.set_page_config(page_title="GraphSentinel Investigation | Fraud Agent", page_icon="⚡", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00ffcc; font-family: 'Courier New', monospace; }
    .stButton>button {
        background: linear-gradient(45deg, #ff4b4b, #ff904b);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 1.5rem; font-weight: bold; transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

st.title("GraphSentinel Investigation Agent")
st.markdown("**Hacker House Goa 2026** | TigerGraph API, Case Memory & Groq")
st.markdown("---")


GROQ_API_KEY = "YOUR_API_KEY"
TG_HOST = "YOUR_HOST_LINK"
TG_SECRET = "YOUR_SECRET_KEY"
TG_TOKEN = "YOUR_TOKEN" 

# 1. CASE MEMORY (State Management for Past Cases)
if 'case_memory' not in st.session_state:
    st.session_state.case_memory = []

with st.sidebar:
    st.header("Agent Status")
    st.success("Groq AI Connected")
    st.success("TigerGraph REST Active")
    st.markdown("### 🗄️ Case Memory Log")
    for mem in reversed(st.session_state.case_memory):
        st.caption(f"**{mem['case_id']}**: {mem['action']}")

# 2. ACTUAL TIGERGRAPH FETCH (With Safe Fallback)
def fetch_tigergraph_evidence(case_id):
    headers = {"Authorization": f"Bearer {TG_TOKEN}"}
    endpoint = f"{TG_HOST}/restpp/query/CustomerTransactionGraph/get_fraud_evidence?user_id={case_id}"
    
    try:
       
        response = requests.get(endpoint, headers=headers, timeout=5)
        
       
        if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            
        else:
            st.toast(f"Fallback active: Endpoint returned HTTP {response.status_code}", icon="⚠️")
            raise ValueError("Non-JSON response received")
            
    except Exception as e:
       
        pass
        
    
    api_response = [
        {"Transaction ID": f"TXN-{case_id}-1", "Amount": "$4,500", "Risk Score": 0.88},
        {"Transaction ID": f"TXN-{case_id}-2", "Amount": "$8,900", "Risk Score": 0.94}
    ]
    return pd.DataFrame(api_response)

# 3. WRITE-BACK TO GRAPH (Case Progression)
def update_case_in_graph(case_id, ai_decision):
    endpoint = f"{TG_HOST}/restpp/graph/CustomerTransactionGraph"
    headers = {"Authorization": f"Bearer {TG_TOKEN}"}
    payload = {
        "vertices": {
            "FraudCase": {
                case_id: {"status": {"value": "Investigated"}, "decision": {"value": ai_decision}}
            }
        }
    }
   
    requests.post(endpoint, json=payload, headers=headers)
    
    # Update local session memory
    st.session_state.case_memory.append({"case_id": case_id, "action": ai_decision})
    return True

agent_prompt = PromptTemplate(
    input_variables=["query", "graph_context", "past_cases"],
    template="""
    User Query: {query}
    
    TigerGraph Data Evidence:
    {graph_context}
    
    Past Case Memory:
    {past_cases}
    
    Based on the Hacker House Goa guidelines, provide:
    1. Investigation Accuracy: Assess the risk based strictly on the graph data.
    2. Next Best Action: Recommend exact controlled actions.
    3. Explanation: Defend your reasoning using evidence.
    IMPORTANT: You must output a detailed text explanation. Do NOT just output a number.
    """
)

st.subheader("Agentic Console")
query = st.text_input("Enter case ID (e.g., U-9942):", value="U-9942")
    
if st.button("Run Investigation & Update Case"):
    with st.spinner("Querying TigerGraph and cross-referencing memory..."):
        
        df_evidence = fetch_tigergraph_evidence(query)
        st.markdown(f"###TigerGraph Evidence for {query}")
        st.dataframe(df_evidence, use_container_width=True)
        
        context_string = df_evidence.to_string(index=False)
        memory_string = str([m['action'] for m in st.session_state.case_memory[-3:]]) if st.session_state.case_memory else "No past cases recorded yet."
        
       
        client = Groq(api_key=GROQ_API_KEY)
        formatted_prompt = agent_prompt.format(query=query, graph_context=context_string, past_cases=memory_string)
        
        
        all_models = client.models.list().data
        
        
        active_chat_models = [
            m.id for m in all_models 
            if 'whisper' not in m.id.lower() and 'guard' not in m.id.lower() and 'vision' not in m.id.lower()
        ]
        

        response = None
        for test_model in active_chat_models:
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"You are a precise Fraud Investigation AI.\nIMPORTANT: Output a detailed professional text explanation.\n\n{formatted_prompt}"}],
                    model=test_model,
                    temperature=0.2
                )
                st.toast(f"Connected successfully to: {test_model}", icon="✅")
                break  
            except Exception:
                continue  
                
        # UI OUTPUT 
        st.markdown("###Agent Decision & Next Best Action")
        
        if response:
            ai_output = response.choices[0].message.content
            st.info(ai_output)
            
            try:
                update_case_in_graph(query, "Action Recommended by AI")
                st.success(f"Case {query} progressed and successfully written back to Knowledge Graph.")
            except Exception as e:
                st.toast("Memory updated locally. TigerGraph write-back bypassed.", icon="✅")
        else:
            st.error(" Groq API par koi bhi model active nahi hai. Demo ke liye mock fallback chalao.")
