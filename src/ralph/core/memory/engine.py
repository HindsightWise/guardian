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
        
        # Configure embedding model
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        self.index = self._load_index()
        self.feelings_db = self._load_feelings()

    def _load_feelings(self):
        if self.feelings_path.exists():
            with open(self.feelings_path, 'r') as f:
                return json.load(f)
        return {}

    def _load_index(self):
        if self.persist_dir.exists():
            try:
                storage_context = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
                return load_index_from_storage(storage_context)
            except Exception as e:
                logging.error(f"Failed to load index: {e}")
                return None
        return None

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
