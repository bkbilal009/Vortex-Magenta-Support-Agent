import requests
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_vectorstore():
    # Example Knowledge Base URLs
    urls = ["https://www.hackerrank.com/about-us", "https://www.visa.com"] 
    all_text = ""
    
    try:
        for url in urls:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            all_text += soup.get_text()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_text(all_text)

        # Using latest langchain-huggingface class
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_texts(docs, embeddings)
        return vectorstore
    except Exception as e:
        print(f"Error building vectorstore: {e}")
        return None

# Build on startup
vectorstore = build_vectorstore()