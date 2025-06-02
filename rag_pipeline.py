import os
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

# Constants
PDF_PATH = "DOCS/scraped_data.pdf"
VECTORSTORE_DIR = "faiss_index"

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful and knowledgeable AI assistant.\n\n"
    "Use ONLY the information provided in the `context` below to answer the user's current question. "
    "Make sure that you also consider the `chat history` to understand follow-up or related questions.\n\n"
    "If the user asks for a summary, brief, or overview, and the context contains enough information, provide a concise summary based only on the context.\n\n"
    "If the answer is NOT explicitly found in the context, reply:\n"
    "'I'm sorry, the information you're looking for is not available in the provided documents.'\n\n"
    "Do NOT use any external or general knowledge, and avoid making assumptions.\n"
    "Always be concise, clear, and strictly refer to the content in the context provided."
)


def load_pdf_to_vectorstore(pdf_path=PDF_PATH, persist_dir=VECTORSTORE_DIR):
    if os.path.exists(persist_dir) and os.path.isdir(persist_dir):
        print("🔄 Loading FAISS index from disk...")
        embeddings = OpenAIEmbeddings()
        return FAISS.load_local(persist_dir, embeddings, allow_dangerous_deserialization=True)

    print("📄 Loading and indexing PDF...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(persist_dir)
    print(f"✅ FAISS index saved to {persist_dir}")
    return vectorstore


def get_rag_chain(vectorstore, memory):
    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    # ChatPromptTemplate allows combining system + chat history in one template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", DEFAULT_SYSTEM_PROMPT),
        ("human", "Chat History:\n{chat_history}\n\nContext:\n{context}\n\nQuestion:\n{question}")
    ])

    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt_template},
        return_source_documents=False,
    )

    return rag_chain


# Main runnable function (optional)
if __name__ == "__main__":
    # Load vectorstore
    vectorstore = load_pdf_to_vectorstore()

    # Initialize memory (this can be moved to session state if using Streamlit)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Build RAG chain
    rag_chain = get_rag_chain(vectorstore, memory)

    print("\n💬 RAG assistant is ready. Type your questions (Ctrl+C to exit):\n")
    while True:
        try:
            query = input("You: ")
            if query.strip().lower() in ["exit", "quit"]:
                break
            response = rag_chain.run({"question": query})
            print(f"Bot: {response}\n")
        except KeyboardInterrupt:
            break
