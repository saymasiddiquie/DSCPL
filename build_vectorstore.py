import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import json

# Vector store path
DB_FAISS_PATH = "vectorstore/db_bible"

# Create directories if they don't exist
os.makedirs(DB_FAISS_PATH, exist_ok=True)

def create_bible_vectorstore():
    """Create a vector store from Bible data"""
    try:
        # Initialize embedding model
        embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        
        # Load Bible data
        with open('bible_data.json', 'r', encoding='utf-8') as f:
            bible_data = json.load(f)
        
        # Prepare documents from Bible data
        texts = []
        metadatas = []
        for book in bible_data['books']:
            for chapter in book['chapters']:
                for verse_idx, verse in enumerate(chapter['verses']):
                    text = f"{verse} ({book['name']} {chapter['number']}:{verse_idx + 1})"
                    metadata = {
                        'book': book['name'],
                        'chapter': chapter['number'],
                        'verse': verse_idx + 1
                    }
                    texts.append(text)
                    metadatas.append(metadata)
        
        # Create vector store
        db = FAISS.from_texts(
            texts=texts,
            embedding=embedding_model,
            metadatas=metadatas
        )
        
        # Save vector store
        db.save_local(DB_FAISS_PATH)
        print(f"Vector store saved to {DB_FAISS_PATH}")
        return db
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None

if __name__ == "__main__":
    create_bible_vectorstore()
