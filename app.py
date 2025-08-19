import os
import subprocess
import streamlit as st
import requests
import time
import gdown  # pip install gdown

# --------------------
# Setup before UI loads
# --------------------
@st.cache_resource  # run only once per Streamlit session
def setup_environment():
    st.write(" Setting up environment...")

    # 1. Download folder from Google Drive
    google_drive_url = "https://drive.google.com/drive/folders/1oRxyT13I_0dxJMHNYC7tQy1jhSBPS_IM"
    gdown.download_folder(google_drive_url, output="AssignmentCAI", quiet=False, use_cookies=False)

    # 2. Install dependencies
    req_path = "AssignmentCAI/requirements.txt"
    if os.path.exists(req_path):
        subprocess.run(
            ["python", "-m", "pip", "install", "-r", req_path],
            check=True
        )

    # 3. Start Flask backend in background
    flask_file = os.path.join("AssignmentCAI", "main", "Flask.py")
    if os.path.exists(flask_file):
        subprocess.Popen(
            ["python", "Flask.py"],
            cwd="AssignmentCAI/main",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    return True

# Run setup once
setup_environment()

# --------------------
# Streamlit UI
# --------------------
st.title("RAG & Fine-Tuned QA Interface")

mode = st.radio("Select Mode", ["RAG", "Fine-Tuned"], key="mode_selector")
user_query = st.text_area("Enter your question:", key="user_query")

if st.button("Ask", key="ask_button"):
    api_url = "http://localhost:5050/ask"
    payload = {"query": user_query, "mode": mode.lower()}

    try:
        start = time.time()
        response = requests.post(api_url, json=payload, timeout=800)
        client_elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            st.markdown(f"**Answer:** {data.get('answer', '')}")
            st.markdown(f"**Method:** {data.get('source', '')}")

            if "confidence_score" in data:
                st.markdown(f"**Confidence Score:** {data['confidence_score']:.3f}")

            if "retrieved_time" in data:
                st.markdown(f"**Server Retrieval Time:** {data['retrieved_time']:.3f} sec")

            st.markdown(f"**Total Response Time:** {client_elapsed:.3f} sec")

            if "factual" in data:
                st.markdown(f"**Factual:** {data['factual']}")

            if "chunks" in data:
                st.markdown("**Retrieved Chunks:**")
                st.json(data['chunks'])
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Request failed: {e}")
