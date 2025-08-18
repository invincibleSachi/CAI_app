import streamlit as st
import requests
import time

## To run this app, use the command:
### streamlit run main/app.py
st.title("RAG & Fine-Tuned QA Interface")

mode = st.radio("Select Mode", ["RAG", "Fine-Tuned"])
user_query = st.text_area("Enter your question:")

if st.button("Ask"):
    start = time.time()
    api_url = "http://localhost:5050/ask"
    payload = {"query": user_query, "mode": mode.lower()}
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        elapsed = time.time() - start
        if response.status_code == 200:
            data = response.json()
            st.markdown(f"**Answer:** {data.get('answer', '')}")
            st.markdown(f"**Method:** {data.get('source', '')}")
            st.markdown(f"**Factual:** {data.get('factual', '')}")
            st.markdown(f"**Retrieved Chunks:** {data.get('chunks', '')}")
            # Confidence: use factual as a proxy, or add a score in your API
            st.markdown(f"**Confidence:** {'High' if data.get('factual') else 'Low'}")
            st.markdown(f"**Response Time:** {elapsed:.2f} seconds")
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Request failed: {e}")