# GraphSentinel - Agentic Fraud Investigation
**Hacker House Goa 2026 Submission**

GraphSentinel is an AI-driven Fraud Investigation Agent that connects to a TigerGraph database to analyze transaction networks, assess risk, and recommend the Next Best Action for uncertain fraud signals.

## Features
* **Dynamic LLM Routing (Groq):** Automatically fetches and connects to the most capable active text model (Llama/Gemma), bypassing deprecation errors.
* **GraphRAG Pipeline:** Injects raw TigerGraph knowledge graph data directly into the AI prompt.
* **Case Memory & Write-back:** Logs decisions and writes them back to the graph to improve future investigations.

## Installation
1. `pip install -r requirements.txt`
2. Add your Groq API key and TigerGraph token in `app.py`.
3. Run the dashboard: `streamlit run app.py`
