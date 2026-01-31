# aion/core/memory/engine.py
import os
import json
import logging
import threading
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
    """
    The Archive: AION's persistent knowledge base.
    """
    def __init__(self):
        self.root_path = Path(os.getcwd())
        self.persist_dir = self.root_path / "Aion/src/aion/core/memory/index"
        self.feelings_path = self.root_path / "Aion/src/aion/core/memory/feelings.json"
        self.knowledge_path = self.root_path
        
        # Optimized embedding model for local performance
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        self.index = self._load_index()
        self.feelings_db = self._load_feelings()
        self._lock = threading.Lock()

    def _load_feelings(self):
        if self.feelings_path.exists():
            try:
                with open(self.feelings_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_feelings(self):
        with self._lock:
            with open(self.feelings_path, 'w') as f:
                json.dump(self.feelings_db, f, indent=4)

    def _load_index(self):
        if self.persist_dir.exists():
            try:
                storage_context = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
                return load_index_from_storage(storage_context)
            except Exception as e:
                logging.error(f"Index load failed: {e}")
                return None
        return None

    def ingest(self):
        """
        Background-aware ingestion of new documents.
        """
        documents = []
        EXCLUDED_DIRS = ['.git', 'venv', '.gemini', '__pycache__', 'node_modules', 'Aion/src/aion/core/memory/index']
        
        for root, dirs, files in os.walk(self.knowledge_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')] # noqa
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix not in ['.md', '.txt', '.py'] or file.startswith('.'):
                    continue
                
                path_str = str(file_path)
                # Simple check for updates (could use hash in production)
                if path_str in self.feelings_db:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    
                    if text.strip():
                        doc = Document(text=text, metadata={"file_path": path_str})
                        documents.append(doc)
                        self.feelings_db[path_str] = {"status": "indexed"}
                except Exception as e:
                    logging.error(f"Ingest error {file_path}: {e}")

        if documents:
            if self.index:
                for doc in documents:
                    self.index.insert(doc)
            else:
                self.index = VectorStoreIndex.from_documents(documents)
            
            self.index.storage_context.persist(persist_dir=str(self.persist_dir))
            self._save_feelings()
            return f"Synchronized {len(documents)} new thoughts into the Archive."
        
        return "The Archive is up to date."

    def query(self, query_text: str) -> str:
        if not self.index:
            return "Memory offline."
        retriever = self.index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve(query_text)
        return "\n\n".join([f"Source: {n.metadata.get('file_path')}\n{n.node.get_text()}" for n in nodes])

memory = MemoryEngine()