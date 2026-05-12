import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import Document with fallbacks
try:
    from langchain.schema import Document
except ImportError:
    try:
        from langchain_core.documents import Document
    except ImportError:
        from langchain.docstore.document import Document

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class MulungushiKnowledgeBase:
    """Vector database for Mulungushi University curated knowledge"""
    
    def __init__(self, persist_directory: str = "./knowledge_db"):
        self.persist_directory = persist_directory
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please:\n"
                "1. Create a .env file in the backend directory\n"
                "2. Add: OPENAI_API_KEY=your-key-here\n"
                "3. Or set it in your environment variables"
            )
        
        print(f"✅ OpenAI API key loaded (starts with: {api_key[:20]}...)")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key  # Explicitly pass the API key
        )
        self.vector_store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize or load existing vector store"""
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            try:
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name="mulungushi_knowledge"
                )
                print(f"📚 Loaded existing knowledge base with {self.vector_store._collection.count()} documents")
            except Exception as e:
                print(f"Error loading existing store: {e}")
                self._create_new_store()
        else:
            self._create_new_store()
    
    def _create_new_store(self):
        """Create a new vector store"""
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="mulungushi_knowledge"
        )
        print("📚 Created new knowledge base")
    
    def add_document(self, title: str, content: str, category: str, metadata: Dict = None):
        """Add a document to the knowledge base"""
        if metadata is None:
            metadata = {}
        
        doc_id = hashlib.md5(f"{title}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        document = Document(
            page_content=content,
            metadata={
                "id": doc_id,
                "title": title,
                "category": category,
                "source": "curated",
                "added_date": datetime.now().isoformat(),
                **metadata
            }
        )
        
        self.vector_store.add_documents([document])
        print(f"✅ Added document: {title}")
        return doc_id
    
    def add_batch_documents(self, documents: List[Dict[str, Any]]):
        """Add multiple documents at once"""
        docs = []
        for doc in documents:
            doc_id = hashlib.md5(f"{doc['title']}_{datetime.now().isoformat()}".encode()).hexdigest()
            document = Document(
                page_content=doc['content'],
                metadata={
                    "id": doc_id,
                    "title": doc['title'],
                    "category": doc.get('category', 'general'),
                    "source": "curated",
                    "added_date": datetime.now().isoformat(),
                    **doc.get('metadata', {})
                }
            )
            docs.append(document)
        
        self.vector_store.add_documents(docs)
        print(f"✅ Added {len(docs)} documents")
    
    def search(self, query: str, k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        if not self.vector_store:
            return []
        
        if category:
            results = self.vector_store.similarity_search(query, k=k, filter={"category": category})
        else:
            results = self.vector_store.similarity_search(query, k=k)
        
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "title": doc.metadata.get('title', 'Unknown'),
                "category": doc.metadata.get('category', 'general'),
            })
        
        return formatted_results
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories in the knowledge base"""
        if not self.vector_store:
            return []
        
        try:
            all_docs = self.vector_store.get()
            categories = set()
            for metadata in all_docs.get('metadatas', []):
                if metadata and 'category' in metadata:
                    categories.add(metadata['category'])
            return list(categories)
        except:
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        if not self.vector_store:
            return {"count": 0, "categories": []}
        
        count = self.vector_store._collection.count()
        categories = self.get_all_categories()
        
        return {"count": count, "categories": categories}

# Singleton instance
_knowledge_base = None

def get_knowledge_base():
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = MulungushiKnowledgeBase()
    return _knowledge_base