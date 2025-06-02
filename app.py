import streamlit as st
import os
from scraper_and_pdf_generator import WikipediaScraperPDFGenerator
from rag_pipeline import load_pdf_to_vectorstore, get_rag_chain
from langchain.memory import ConversationBufferMemory

# --- Page Setup ---
st.set_page_config(page_title="Gen AI RAG Assistant", layout="centered")

# --- Sidebar: API Key ---
with st.sidebar:
    st.markdown("## 🔐 API Configuration")
    openai_key = st.text_input("Enter OpenAI API Key", type="password", placeholder="sk-...")
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    else:
        st.warning("🔑 Please enter your OpenAI API key above.", icon="⚠️")

# --- Title ---
st.markdown("<h1 style='text-align: center;'>🤖 Gen AI RAG Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>An AI assistant powered by Wikipedia + RAG with memory</p>", unsafe_allow_html=True)
st.divider()

# --- Step 1: PDF Generation ---
st.markdown("### 📄 Step 1: Generate Knowledge Base PDF")
with st.expander("📘 Wikipedia sources used"):
    st.markdown("""
    - [Generative AI](https://en.wikipedia.org/wiki/Generative_artificial_intelligence)  
    - [Artificial General Intelligence (AGI)](https://en.wikipedia.org/wiki/Artificial_general_intelligence)  
    - [Retrieval-Augmented Generation (RAG)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)  
    - [Large Language Models (LLMs)](https://en.wikipedia.org/wiki/Large_language_model)  
    """)

pdf_generated = False
if st.button("📝 Generate PDF"):
    if not openai_key:
        st.error("❌ OpenAI API key is required to proceed.")
    else:
        scraper = WikipediaScraperPDFGenerator()
        pdf_path = scraper.run()
        st.success("✅ Wikipedia content saved to PDF.")
        pdf_generated = True
        with open(pdf_path, "rb") as f:
            st.download_button(label="📥 Download PDF", data=f, file_name="scraped_data.pdf")

st.divider()

# --- Step 2: Load Vectorstore and Setup Chain ---
pdf_path = "DOCS/scraped_data.pdf"
if openai_key and os.path.exists(pdf_path):
    if "rag_chain" not in st.session_state:
        with st.spinner("🧠 Loading vectorstore and initializing assistant..."):
            vectorstore = load_pdf_to_vectorstore(pdf_path)

            # Create memory once and store in session
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            st.session_state.memory = memory

            st.session_state.rag_chain = get_rag_chain(vectorstore, memory)
            st.session_state.chat_history = []

# --- Step 3: Ask Questions ---
st.markdown("### 🔎 Step 2: Ask Questions (with Memory)")
query = st.text_input("💬 Ask your question:", placeholder="e.g. What is AGI?")

if query:
    if not openai_key:
        st.error("❌ API key required.")
    elif "rag_chain" not in st.session_state:
        st.warning("📄 Please generate the PDF before asking questions.", icon="⚠️")
    else:
        with st.spinner("🧠 Thinking..."):
            try:
                result = st.session_state.rag_chain.run({"question": query})
                st.session_state.chat_history.append(("You", query))
                st.session_state.chat_history.append(("Assistant", result))
                st.success("✅ Answer generated")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --- Chat History Display ---
if "chat_history" in st.session_state and st.session_state.chat_history:
    st.markdown("### 🗂️ Conversation History")
    for speaker, text in st.session_state.chat_history:
        if speaker == "You":
            st.markdown(f"**🧑 You:** {text}")
        else:
            st.markdown(f"**🤖 Assistant:** {text}")

# --- Footer ---
st.divider()
st.markdown(
    "<p style='text-align: center; color: grey; font-size: 0.9em;'>Built with ❤️ using Streamlit, LangChain, and OpenAI</p>",
    unsafe_allow_html=True
)
