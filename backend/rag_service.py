"""
RAG Service Module - Document loading, chunking, embedding and retrieval
"""
import os
from pathlib import Path
from typing import List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


class RAGService:
    """RAG Service: Manage knowledge base documents loading, indexing and retrieval"""

    def __init__(
            self,
            knowledge_dir: str = "./data/knowledge",
            persist_dir: str = "./data/chroma",
            chunk_size: int = 500,
            chunk_overlap: int = 50
    ):
        self.knowledge_dir = Path(knowledge_dir)
        self.persist_dir = Path(persist_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Init embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "，", " ", ""]
        )
        
        # Vector store
        self.vector_store = None

    def load_documents(self) -> List[Dict[str, str]]:
        """Load all txt files from knowledge directory"""
        documents = []

        if not self.knowledge_dir.exists():
            return documents

        txt_files = list(self.knowledge_dir.glob("*.txt"))

        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        documents.append({
                            'content': content,
                            'source': file_path.name
                        })
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")

        return documents
    
    def build_index(self) -> bool:
        """Build vector index: load docs -> chunk -> embed -> store"""
        # 1. Load documents
        documents = self.load_documents()
        if not documents:
            print("No documents to index")
            return False
        
        # 2. Chunk documents
        texts = []
        metadatas = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc['content'])
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append({
                    'source': doc['source'],
                    'chunk_index': i
                })
        
        print(f"Loaded {len(documents)} docs, {len(texts)} chunks")
        
        # 3. Create vector store
        self.vector_store = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=str(self.persist_dir)
        )
        
        # 4. Persist
        self.vector_store.persist()
        print(f"Index saved to {self.persist_dir}")
        
        return True
    
    def load_index(self) -> bool:
        """Load existing vector index"""
        if not self.persist_dir.exists():
            return False
        
        try:
            self.vector_store = Chroma(
                persist_directory=str(self.persist_dir),
                embedding_function=self.embeddings
            )
            return True
        except Exception as e:
            print(f"Load index failed: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search relevant document chunks"""
        if not self.vector_store:
            if not self.load_index():
                return []
        
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=top_k
        )
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'content': doc.page_content,
                'source': doc.metadata.get('source', 'unknown'),
                'score': float(score)
            })
        
        return formatted_results


# Singleton
_rag_service = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


if __name__ == "__main__":
    service = RAGService()
    service.build_index()
    results = service.search("shipping cost", top_k=3)
    for r in results:
        print(f"{r['source']}: {r['content'][:100]}...")
