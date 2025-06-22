import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

def build_vectorstore():
    """Build FAISS vector store with Bible data"""
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    
    # Load processed Bible data
    with open('processed_bible_data.json', 'r', encoding='utf-8') as f:
        bible_data = json.load(f)
    
    # Create documents from Bible data
    texts = []
    metadatas = []
    
    for book in bible_data:
        for verse_idx, verse in enumerate(book['verses']):
            text = f"{verse} (Book {book['book']} Chapter {book['chapter']})"
            texts.append(text)
            metadatas.append({
                'book': book['book'],
                'chapter': book['chapter'],
                'verse_number': verse_idx + 1
            })
    
    # Create vector store
    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )
    
    # Save vector store
    vectorstore.save_local("vectorstore/bible_vectorstore")
    print("Vector store created successfully!")

if __name__ == "__main__":
    build_vectorstore()
