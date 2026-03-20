import streamlit as st
import requests

st.set_page_config(page_title="RAG Assistant", layout="wide")

# 🔥 Header
st.title("🤖 RAG Document Assistant")
st.caption("Ask questions about your documents and get answers with sources")

# Sidebar settings
st.sidebar.header("⚙️ Settings")
top_k = st.sidebar.slider("Top K Retrieval", 1, 10, 3)
show_debug = st.sidebar.checkbox("Show Debug Info", value=False)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
query = st.chat_input("💬 Ask something about your documents...")

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8001/query",
                    json={"query": query, "top_k": top_k},
                    timeout=60
                )

                # 🔥 Backend status check
                if response.status_code != 200:
                    st.error(f"Backend error: {response.status_code}")
                    st.write(response.text)
                    st.stop()

                # 🔥 Safe JSON parsing
                try:
                    data = response.json()
                except Exception:
                    st.error("⚠️ Backend returned invalid response")
                    st.write(response.text)
                    st.stop()

                # Extract fields
                answer = data.get("answer", "No answer returned")
                sources = data.get("sources", [])
                confidence = data.get("confidence", 0)

                # 🔥 Answer section
                st.divider()
                st.markdown("### 🤖 Answer")
                st.info(answer)

                # 🔥 Confidence (cleaner)
                conf = int(min(max(confidence, 0), 1) * 100)
                st.markdown(f"**Confidence:** {conf}%")
                st.progress(conf / 100)

                # 🔥 Sources (collapsible)
                if sources:
                    st.markdown("## 📚 Sources")

                    for i, src in enumerate(sources):
                        with st.expander(f"📄 Source {i+1} — {src.get('document', 'Unknown')}"):
                            st.code(src.get("content", ""), language="text")

                # Debug info
                if show_debug:
                    st.json(data)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")