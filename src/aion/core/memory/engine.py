# ralph/core/memory/engine.py
import os
import json
import logging
from pathlib import Path
from striprtf.striprtf import rtf_to_text

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Document,
    Settings,
)
from llama_index.readers.file import PDFReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class MemoryEngine:
    def __init__(self):
        self.root_path = Path(os.getcwd())
        self.persist_dir = self.root_path / "guardian/src/ralph/core/memory/index"
        self.feelings_path = self.root_path / "guardian/src/ralph/core/memory/feelings.json"
        self.knowledge_path = self.root_path  # Scan from root
        
        # Configure embedding model
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        self.index = self._load_index()
        self.feelings_db = self._load_feelings()

    def _load_feelings(self):
        if self.feelings_path.exists():
            with open(self.feelings_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_feelings(self):
        with open(self.feelings_path, 'w') as f:
            json.dump(self.feelings_db, f, indent=4)

    def _load_index(self):
        if self.persist_dir.exists():
            try:
                storage_context = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
                return load_index_from_storage(storage_context)
            except Exception as e:
                logging.error(f"Failed to load index: {e}")
                return None
        return None

    def ingest(self):
        """
        Scans the knowledge directory and updates the index.
        """
        documents = []
        # Basic exclusion list
        EXCLUDED_DIRS = ['.git', 'venv', '.gemini', '__pycache__', 'node_modules']
        EXCLUDED_FILES = ['.DS_Store', 'package-lock.json', 'yarn.lock']

        for root, dirs, files in os.walk(self.knowledge_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in files:
                if file in EXCLUDED_FILES or file.startswith('.'):
                    continue
                
                file_path = Path(root) / file
                if file_path.suffix not in ['.md', '.txt', '.py']:
                    continue

                try:
                    # Simple duplicate check using file path as key
                    if str(file_path) in self.feelings_db: 
                        # In a real system, we'd check modification time or hash
                        continue

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    
                    if not text.strip():
                        continue

                    doc = Document(text=text, metadata={"file_path": str(file_path)})
                    documents.append(doc)
                    self.feelings_db[str(file_path)] = {"status": "indexed"}
                    
                except Exception as e:
                    logging.error(f"Error reading {file_path}: {e}")

        if documents:
            if self.index:
                for doc in documents:
                    self.index.insert(doc)
            else:
                self.index = VectorStoreIndex.from_documents(documents)
            
            self.index.storage_context.persist(persist_dir=str(self.persist_dir))
            self._save_feelings()
            return f"Ingested {len(documents)} new documents."
        
        return "No new documents to ingest."

    def query(self, query_text: str) -> str:
        """
        Retrieves relevant context from the vector store.
        """
        if not self.index:
            return "Memory index not initialized."
            
        retriever = self.index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve(query_text)
        
        context = []
        for node in nodes:
            # Try to get the file path or some identifier
            source = node.metadata.get("file_path", "Unknown Source")
            excerpt = node.node.get_text()
            context.append(f"Source: {source}\nContent: {excerpt}")
            
        return "\n\n".join(context)

# Singleton instance
memory = MemoryEngine()
