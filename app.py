# app.py

import streamlit as st
import os
from scraper_and_pdf_generator import WikipediaScraperPDFGenerator
from rag_pipeline import load_pdf_to_vectorstore, get_rag_chain

st.set_page_config(page_title="Gen AI RAG App", layout="centered")
st.title("🤖 Gen AI RAG Assistant")

# --- Section 0: OpenAI Key Input ---
st.subheader("🔐 Enter OpenAI API Key")
openai_key = st.text_input("Your OpenAI API Key", type="password")

if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
else:
    st.warning("Please enter your OpenAI API key to continue.")

# --- Section 1: PDF Generator ---
st.subheader("📄 Step 1: Generate PDF from Wikipedia Articles")

if st.button("📝 Generate Wikipedia PDF"):
    if not openai_key:
        st.error("❌ OpenAI API key is required to generate the PDF and use RAG.")
    else:
        scraper = WikipediaScraperPDFGenerator()
        pdf_path = scraper.run()
        st.success(f"✅ PDF generated at `{pdf_path}`")

        with open(pdf_path, "rb") as f:
            st.download_button(label="📥 Download PDF", data=f, file_name="scraped_data.pdf")

# --- Section 2: Query Input and RAG Processing ---
st.subheader("🔎 Step 2: Ask a Question (RAG)")

query = st.text_input("Enter your query here")

if query:
    if not openai_key:
        st.error("❌ Please enter your OpenAI API key above before querying.")
    else:
        with st.spinner("🔍 Processing your query with RAG..."):
            try:
                vectorstore = load_pdf_to_vectorstore()
                rag_chain = get_rag_chain(vectorstore)
                result = rag_chain.run(query)
                st.success("✅ Response Generated")
                st.markdown(f"**Answer:**\n\n{result}")
            except Exception as e:
                st.error(f"❌ Error during RAG processing: {e}")
